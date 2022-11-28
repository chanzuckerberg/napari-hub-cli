# https://api.napari-hub.org/plugins

import csv
from pathlib import Path

import requests
from git import GitCommandError
from git.repo import Repo
from rich.progress import Progress, TaskID

from ..constants import NAPARI_HUB_API_URL
from ..utils import (
    LocalDirectory,
    NonExistingNapariPluginError,
    TemporaryDirectory,
    get_repository_url,
)
from .metadata_checklist import (
    AnalysisStatus,
    PluginAnalysisResult,
    create_checklist,
    display_checklist,
)


class FakeProgress(object):
    def start(self):
        ...

    def stop(self):
        ...

    def add_task(self, *args, **kwargs):
        return TaskID(0)

    def update(self, *args, **kwargs):
        ...


def analyse_remote_plugin(
    plugin_name,
    api_url=NAPARI_HUB_API_URL,
    display_info=False,
    cleanup=True,
    directory=None,
):
    """Launch the analysis of a remote plugin using the plugin name.
    The analyser automatically clones the plugin repository and performs the analysis.

    Parameters
    ----------
    plugin_name: str
        The plugin name to analyse.

    api_url: Optional[str] = NAPARI_HUB_API_LINK
        The Napari HUB api url, default value is NAPARI_HUB_API_LINK from the 'napari_hub_cli.constants' module

    cleanup: Optional[bool] = True
        Should the analysis directory be deleted after analysis. If not, responsibility is let to the user to delete the
        directory.

    display_info: Optional[bool] = False
        If activated, a progress bar will display information about the running operation

    directory: Optional[Path|str] = None
        In which directory the repository should be cloned. If not set, a tmp directory is automatically created in the
        tmp folder of the system.
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
        return analyse_remote_plugin_url(
            plugin_name,
            plugin_url,
            display_info=display_info,
            cleanup=cleanup,
            directory=directory,
        )
    except NonExistingNapariPluginError as e:
        print(e.message)
        return PluginAnalysisResult.with_status(AnalysisStatus.NON_EXISTING_PLUGIN)


def analyse_remote_plugin_url(
    plugin_name,
    plugin_url,
    display_info=False,
    cleanup=True,
    directory=None,
):
    directory = (
        LocalDirectory(Path(directory), cleanup)
        if directory
        else TemporaryDirectory(delete=cleanup)
    )

    with directory as tmpdirname:
        tmp_dir = Path(tmpdirname)
        test_repo = tmp_dir / plugin_name

        p = Progress() if display_info else FakeProgress()
        p.start()
        task = p.add_task(
            f"Cloning repository [bold green]{plugin_name}[/bold green] - [green]{plugin_url}[/green] in [red]{test_repo}[/red]",
            visible=display_info,
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
            result = create_checklist(test_repo)
            result.url = plugin_url  # update the plugin url
            p.stop()
            return result
        except GitCommandError:
            return PluginAnalysisResult.with_status(
                AnalysisStatus.BAD_URL, url=plugin_url
            )


def display_remote_analysis(plugin_name, api_url=NAPARI_HUB_API_URL):
    result = analyse_remote_plugin(plugin_name, api_url=api_url, display_info=True)
    display_checklist(result)
    _display_error_message(plugin_name, result)
    return result.status == AnalysisStatus.SUCCESS


def analyze_all_remote_plugins(
    api_url=NAPARI_HUB_API_URL, display_info=False, directory=None
):
    all_results = {}
    plugins_name = requests.get(api_url).json().keys()
    total = len(plugins_name)
    description = "Analysing all plugins in Napari-HUB repository..."
    with Progress() as p:
        task = p.add_task(description, visible=display_info)
        for name in plugins_name:
            result = analyse_remote_plugin(
                name, display_info=False, directory=directory
            )
            all_results[name] = result
            p.update(
                task,
                total=total,
                advance=1,
                description=f"{description} (checking {name!r})",
            )
            if not display_info:
                continue
            _display_error_message(name, result)

    return all_results


def _display_error_message(plugin_name, result):
    if result.status is AnalysisStatus.BAD_URL:
        print(
            f"\N{BALLOT X} Repository URL format for plugin {plugin_name!r} is wrong (url: {result.url})"
        )
    elif result.status is AnalysisStatus.MISSING_URL:
        print(
            f"\N{BALLOT X} Plugin {plugin_name!r} does not have repository URL on the Naparay-HUB plateform"
        )
    elif result.status is AnalysisStatus.UNACCESSIBLE_REPOSITORY:
        print(
            f"\N{BALLOT X} Repository URL for plugin {plugin_name!r} is not accessible (private repository?) (url: {result.url})"
        )


def build_csv_dict(dict_results):
    if not dict_results:
        return []

    rows = []
    for plugin_name, analysis_result in dict_results.items():
        row = {
            "Plugin Name": plugin_name,
            "Analysis Status": analysis_result.status.name,
            "Repository URL": analysis_result.url,
        }
        for feature in analysis_result.features:
            row[feature.meta.name] = feature.found
            if feature.has_fallback_files:
                row[f"{feature.meta.name} in fallback"] = feature.only_in_fallback
        rows.append(row)
    return rows


def write_csv(rows, output_filename):
    if not rows:
        return

    first_entry = rows[0]
    headers = first_entry.keys()
    with open(output_filename, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
