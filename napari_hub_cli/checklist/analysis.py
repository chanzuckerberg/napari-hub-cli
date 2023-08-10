# https://api.napari-hub.org/plugins

import csv
from pathlib import Path
from textwrap import dedent
from rich import print

import requests
from git import GitCommandError
from git.repo import Repo
from rich.progress import Progress, TaskID

from ..constants import NAPARI_HUB_API_URL
from ..utils import (
    LocalDirectory,
    NonExistingNapariPluginError,
    TemporaryDirectory,
    get_all_napari_plugin_names,
    get_repository_url,
)
from .metadata import (
    AnalysisStatus,
    PluginAnalysisResult,
    analyse_local_plugin,
    display_checklist,
)
from .projectmetadata import project_metadata_suite

DEFAULT_SUITE = project_metadata_suite


class FakeProgress(object):
    def start(self):
        ...

    def stop(self):
        ...

    def add_task(self, *args, **kwargs):
        return TaskID(0)

    def update(self, *args, **kwargs):
        ...

    def start_task(self, *args, **kwargs):
        ...


def analyse_remote_plugin(
    plugin_name,
    requirements_suite=DEFAULT_SUITE,
    api_url=NAPARI_HUB_API_URL,
    display_info=False,
    cleanup=True,
    directory=None,
    progress_bar=None,
    **kwargs,
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
    title, _ = requirements_suite
    try:
        plugin_url = get_repository_url(plugin_name, api_url=api_url)
        if not plugin_url:
            return PluginAnalysisResult.with_status(
                AnalysisStatus.MISSING_URL, title=title
            )

        access = requests.get(plugin_url)
        if access.status_code != 200:
            return PluginAnalysisResult.with_status(
                AnalysisStatus.UNACCESSIBLE_REPOSITORY,
                url=plugin_url,
                title=title,
            )
        return analyse_remote_plugin_url(
            plugin_name,
            plugin_url,
            requirements_suite=requirements_suite,
            display_info=display_info,
            cleanup=cleanup,
            directory=directory,
            progress_bar=progress_bar,
            **kwargs,
        )
    except NonExistingNapariPluginError as e:
        print(e.message)
        return PluginAnalysisResult.with_status(
            AnalysisStatus.NON_EXISTING_PLUGIN, title=title
        )


def analyse_remote_plugin_url(
    plugin_name,
    plugin_url,
    requirements_suite=DEFAULT_SUITE,
    display_info=False,
    cleanup=True,
    directory=None,
    progress_bar=None,
    **kwargs,
):
    directory = (
        LocalDirectory(Path(directory), cleanup)
        if directory
        else TemporaryDirectory(delete=cleanup)
    )
    title, suite_gen = requirements_suite

    with directory as tmpdirname:
        tmp_dir = Path(tmpdirname)
        test_repo = tmp_dir / plugin_name
        if progress_bar:
            p = progress_bar
            display_info = True
        else:
            p = Progress(transient=True) if display_info else FakeProgress()
            p.start()
        started = False
        task = None

        def update_task(_, step, total, *__):
            nonlocal started, task
            if not started:
                started = True
                task = p.add_task(
                    f"Cloning repository [bold green]{plugin_name}[/bold green] - [green]{plugin_url}[/green] in [red]{test_repo}[/red]",
                    visible=display_info,
                    total=total,
                )
                p.start_task(task)
            p.update(
                task,  # type: ignore
                total=total,
                advance=step,
            )

        try:
            Repo.clone_from(plugin_url, test_repo, depth=1, progress=update_task)
        except GitCommandError:
            if not test_repo.exists():
                return PluginAnalysisResult.with_status(
                    AnalysisStatus.BAD_URL, url=plugin_url, title=title
                )
        result = analyse_local_plugin(test_repo, suite_gen, progress_task=p, **kwargs)
        result.url = plugin_url  # update the plugin url
        if not progress_bar:
            p.stop()
        return result


def display_remote_analysis(
    plugin_name, requirements_suite=DEFAULT_SUITE, api_url=NAPARI_HUB_API_URL, **kwargs
):
    result = analyse_remote_plugin(
        plugin_name, requirements_suite, api_url=api_url, display_info=True, **kwargs
    )
    display_checklist(result)
    _display_error_message(plugin_name, result)
    return result.status == AnalysisStatus.SUCCESS


def analyze_remote_plugins(
    all_plugins=False,
    plugins_name=None,
    requirements_suite=DEFAULT_SUITE,
    api_url=NAPARI_HUB_API_URL,
    display_info=False,
    directory=None,
    **kwargs,
):
    all_results = {}
    if all_plugins:
        plugins_name = get_all_napari_plugin_names(api_url)
    else:
        plugins_name = plugins_name or []
    total = len(plugins_name)
    print(f"Selected plugins: {'all' if all_plugins else plugins_name}")
    description = "Analysing plugins in napari hub repository..."
    with Progress(transient=True) as p:
        task = p.add_task(description, visible=display_info, total=total)
        for name in plugins_name:
            result = analyse_remote_plugin(
                name,
                requirements_suite,
                display_info=False,
                directory=directory,
                progress_bar=p,
                **kwargs,
            )
            all_results[name] = result
            p.update(
                task,
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
            f"\N{BALLOT X} Plugin {plugin_name!r} does not have a repository URL on the napari hub platform"
        )
    elif result.status is AnalysisStatus.UNACCESSIBLE_REPOSITORY:
        print(
            f"\N{BALLOT X} Repository URL for plugin {plugin_name!r} is not accessible (private repository?) (url: {result.url})"
        )


# Shamefully copied from stackoverflow
def n2a(n):
    d, m = divmod(n, 26)  # 26 is the number of ASCII letters
    return "" if n < 0 else n2a(d - 1) + chr(m + 65)  # chr(65) = 'A'


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

        # Reorganize the information to put the "summaries" first
        for feature in (
            f for f in analysis_result.additionals if f.meta.linked_details
        ):
            idx_linked_feature = [a.meta for a in analysis_result.additionals].index(
                feature.meta.linked_details
            )
            num_added_row = 3  # the 3 added row from the line above
            column = len(analysis_result.features) + idx_linked_feature + num_added_row
            result = feature.result
            if "No " not in result:
                result = (
                    dedent(str(result)).strip()
                    + f"\n\nSee details from column {n2a(column)}"
                )
            row[feature.meta.name] = result

        for feature in analysis_result.features:
            row[feature.meta.name] = feature.found
            if feature.has_fallback_files:
                row[f"{feature.meta.name} in fallback"] = feature.only_in_fallback

        for feature in (
            f for f in analysis_result.additionals if not f.meta.linked_details
        ):
            row[feature.meta.name] = feature.result

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
    output_path = Path(output_filename)
    print(
        f"\n [bold white] CSV: {output_filename} successfully created at {output_path.resolve()} \n [/bold white]"
    )
