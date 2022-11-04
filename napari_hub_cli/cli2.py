# https://api.napari-hub.org/plugins

import tempfile
from pathlib import Path

from git import Repo
from rich.progress import Progress

from .constants import NAPARI_HUB_API_LINK
from .utils import NonExistingNapariPluginError, get_repository_url


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

        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_dir = Path(tmpdirname)
            test_repo = tmp_dir / plugin_name

            with Progress() as p:
                task = p.add_task(
                    f"Cloning repository [bold]{plugin_name}[/bold] - {plugin_url} in {test_repo}"
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
            #  |
            #  V
            ...

    except NonExistingNapariPluginError as e:
        print(e.message)
