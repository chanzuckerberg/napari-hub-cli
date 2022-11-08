# https://api.napari-hub.org/plugins

import tempfile
from pathlib import Path

import requests
from git import GitCommandError, Repo
from rich.progress import Progress

from ..constants import NAPARI_HUB_API_LINK
from ..utils import NonExistingNapariPluginError, get_repository_url
from .create_doc_checklist import AnalysisStatus, PluginAnalysisResult, create_checklist


class MissingRepositoryURL(Exception):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__(
            f"Plugin {plugin!r} does not have repository URL on the Napari-HUB plateform"
        )


class NonAccessibleRepositoryURL(Exception):
    def __init__(self, plugin, url):
        self.plugin = plugin
        self.url = url
        super().__init__(
            f"Repository URL {url!r} for plugin {plugin!r} is not accessible (private repository?)"
        )


def analyse_remote_plugin(plugin_name, api_url=NAPARI_HUB_API_LINK):
    """Launch the analysis of a remote plugin using the plugin name.
    The analyser automatically clones the plugin repository and performs the analysis.

    Parameters
    ----------
    plugin_name: str
        The plugin name to analyse.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module
    """
    try:
        plugin_url = get_repository_url(plugin_name, api_url=api_url)
        if not plugin_url:
            return PluginAnalysisResult.with_status(AnalysisStatus.MISSING_URL)

        access = requests.get(plugin_url)
        if access.status_code != 200:
            return PluginAnalysisResult.with_status(
                AnalysisStatus.UNACCESSIBLE_REPOSITORY, url=plugin_url
            )

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_dir = Path(tmpdirname)
            test_repo = tmp_dir / plugin_name

            with Progress() as p:
                task = p.add_task(
                    f"Cloning repository [bold green]{plugin_name}[/bold green] - [green]{plugin_url}[/green] in [red]{test_repo}[/red]"
                )
                try:
                    Repo.clone_from(
                        plugin_url,
                        test_repo,
                        depth=1,
                        progress=lambda _, step, total, *args: p.update(
                            task,
                            total=total,
                            advance=step,
                        ),
                    )
                    # We launch the equivalent of the local analysis here
                    #                |
                    #                V
                    return create_checklist(test_repo)  # if the operation was a success
                except GitCommandError:
                    return PluginAnalysisResult.with_status(
                        AnalysisStatus.BAD_URL, url=plugin_url
                    )
    except NonExistingNapariPluginError as e:
        print(e.message)
        return PluginAnalysisResult.with_status(AnalysisStatus.NON_EXISTING_PLUGIN)


def display_remote_analysis(plugin_name, api_url=NAPARI_HUB_API_LINK):
    result = analyse_remote_plugin(plugin_name, api_url=api_url)
    _display_error_message(plugin_name, result)
    return result.status == AnalysisStatus.SUCCESS


def analyze_all_remote_plugins(api_url=NAPARI_HUB_API_LINK, display_info=False):
    all_results = {}
    plugins_name = requests.get(api_url).json().keys()

    for name in plugins_name:
        result = analyse_remote_plugin(name)
        all_results[name] = result
        if not display_info:
            continue
        _display_error_message(name, result)
    return all_results


def _display_error_message(plugin_name, result):
    if result.status == AnalysisStatus.BAD_URL:
        print(
            f"\N{BALLOT X} Repository URL format for plugin {plugin_name!r} is wrong (url: {result.url})"
        )
    elif result.status == AnalysisStatus.MISSING_URL:
        print(
            f"\N{BALLOT X} Plugin {plugin_name} does not have repository URL on the Naparay-HUB plateform"
        )
    elif result.status == AnalysisStatus.UNACCESSIBLE_REPOSITORY:
        print(
            f"\N{BALLOT X} Repository URL for plugin {plugin_name!r} is not accessible (private repository?) - url: {result.url}"
        )
