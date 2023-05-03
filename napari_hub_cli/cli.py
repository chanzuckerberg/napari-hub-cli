"""Console script for napari_hub_cli.

Exit code status are the following:
* 0 = OK
* 1 = unexisting path
* 2 = missing metadata
* 3 = non-existing plugin in the Napari HUB platform
* 4 = CFF citation file not created
"""

import argparse
import os
import sys

from napari_hub_cli.checklist.analysis import DEFAULT_SUITE

from .checklist import analyse_local_plugin, display_checklist
from .citation import create_cff_citation


def create_citation(plugin_path):
    """Creates the CFF citation for the plugin at args.plugin_path

    Parameters
    ----------
    plugin_path: str
        Local path to your plugin
    Returns
    -------
    int
        the status of the result, 0 = OK, 1 = unexisting path, 4 = CFF file not created
    """

    if not os.path.exists(plugin_path):
        print(f"Nothing found at path: {plugin_path}")
        return 1
    ret = create_cff_citation(plugin_path)
    return 0 if ret else 4


def documentation_checklist(plugin_path):
    """Creates a documentation checklist based on the available metadata for the plugin at args.plugin_path
    Parameters
    ----------
    plugin_path: str
        Local path to your plugin
    i: bool
        Is interactive mode activated
    Returns
    -------
    int
        the status of the result, 0 = OK, 1 = unexisting path, 2 = missing metadata
    """
    if not os.path.exists(plugin_path):
        print(f"Nothing found at path: {plugin_path}")
        return 1
    check_list = analyse_local_plugin(plugin_path, DEFAULT_SUITE)
    display_checklist(check_list)
    return 0


def parse_args(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subcommand = subparsers.add_parser(
        "check-metadata", help="Checks consistency of a local plugin"
    )
    subcommand.add_argument("plugin_path", help="Local path to your plugin")
    subcommand.set_defaults(func=documentation_checklist)

    ## create-cff-citation
    subcommand = subparsers.add_parser(
        "create-citation", help="Creates a CITATION.cff file of a local plugin"
    )
    subcommand.add_argument("plugin_path", help="Local path to your plugin")
    subcommand.set_defaults(func=create_citation)

    return parser.parse_args(args)


def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "func"}
    status_code = args.func(**kwargs)
    exit(status_code)
