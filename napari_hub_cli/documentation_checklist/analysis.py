# https://api.napari-hub.org/plugins

import tempfile
from pathlib import Path

from git import Repo
from regex import P
import requests
from rich.progress import Progress

from ..constants import NAPARI_HUB_API_LINK
from ..utils import NonExistingNapariPluginError, get_repository_url
from .create_doc_checklist import (
    PluginAnalysisResult,
    create_checklist,
    display_checklist,
)


class MissingRepositoryURL(Exception):
    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__(
            f"Plugin {plugin!r} does not have repository URL on the Napari-HUB plateform"
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
            raise MissingRepositoryURL(plugin_name)

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_dir = Path(tmpdirname)
            test_repo = tmp_dir / plugin_name

            with Progress() as p:
                task = p.add_task(
                    f"Cloning repository [bold green]{plugin_name}[/bold green] - [green]{plugin_url}[/green] in [red]{test_repo}[/red]"
                )
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
    except NonExistingNapariPluginError as e:
        print(e.message)
        return PluginAnalysisResult([])


def analyze_all_remote_plugins(api_url=NAPARI_HUB_API_LINK):
    all_results = []
    missing_urls = []
    plugins_name = requests.get(api_url).json().keys()
    for name in plugins_name:
        try:
            all_results.append(analyse_remote_plugin(name))
        except MissingRepositoryURL:
            print(
                f"** Plugin {name} does not have repository URL on the Naparay-HUB plateform"
            )
            missing_urls.append(name)
    return all_results, missing_urls
