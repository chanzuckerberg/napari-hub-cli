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

from .autofix import analyse_plugins_then_create_PR
from .checklist import analyse_local_plugin, display_checklist
from .checklist.analysis import (
    analyze_all_remote_plugins,
    build_csv_dict,
    display_remote_analysis,
    write_csv,
)
from .citation import create_cff_citation
from .utils import get_all_napari_plugin_names


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
    check_list = analyse_local_plugin(plugin_path)
    display_checklist(check_list)
    return 0


def remote_documentation_checklist(plugin_name):
    """Creates a documentation checklist about the available metadata from a plugin of the Napari HUB platform.
    Parameters
    ----------
    plugin_name : str
        Name of the plugin to analyse on the Naparai HUB platform
    Returns
    -------
    int
        the status of the result, 0 = OK, 3 = something went wrong, probably non-existing plugin in the Napari HUB platform
    """
    success = display_remote_analysis(plugin_name)
    return 0 if success else 3


def generate_report_all_plugins(output_csv):
    """Creates a CSV with missing artifacts for all plugins of the Napari HUB platform.
    Returns
    -------
    int
        the status of the result, 0 = OK
    """
    results = analyze_all_remote_plugins(display_info=True)
    rows = build_csv_dict(results)
    write_csv(rows, output_csv)
    return 0


def autofix(plugins, dir, all, push_on_github):
    """
    Returns
    -------
    int
        the status of the result, 0 = OK, 3 = non-existing plugin in the Napari HUB platform
    """
    if all:
        plugins = get_all_napari_plugin_names()

    result = analyse_plugins_then_create_PR(
        plugins, directory=dir, dry_run=not push_on_github
    )
    return 0 if result else 3


def parse_args(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    subcommand = subparsers.add_parser(
        "check-metadata", help="Checks consistency of a local plugin"
    )
    subcommand.add_argument("plugin_path", help="Local path to your plugin")
    subcommand.set_defaults(func=documentation_checklist)

    ## check-plugin
    subcommand = subparsers.add_parser(
        "check-plugin", help="Checks consistency of a remote plugin"
    )
    subcommand.add_argument("plugin_name", help="Name of the plugin in Napari HUB")
    subcommand.set_defaults(func=remote_documentation_checklist)

    ## all-plugin-report
    subcommand = subparsers.add_parser(
        "all-plugins-report",
        help="Generates a CSV report with consistency analysis of all plugins in the Napari-HUB platform",
    )
    subcommand.add_argument("output_csv", help="Output file name (e.g: 'output.csv')")
    subcommand.set_defaults(func=generate_report_all_plugins)

    ## create-cff-citation
    subcommand = subparsers.add_parser(
        "create-citation", help="Creates a CITATION.cff file of a local plugin"
    )
    subcommand.add_argument("plugin_path", help="Local path to your plugin")
    subcommand.set_defaults(func=create_citation)

    ## autofix
    subcommand = subparsers.add_parser(
        "autofix",
        help="Automatically analyse and fixes plugin repositories creating pull requests and issues on Github",
    )
    subcommand.add_argument(
        "-p",
        "--plugins",
        nargs="+",
        help="List of plugins name to automatically audit/fix",
    )
    subcommand.add_argument(
        "-d",
        "--dir",
        help="Working directory in which plugins will be cloned (by default the tmp directory of your OS)",
    )
    subcommand.add_argument(
        "-a",
        "--all",
        default=False,
        action="store_true",
        help="Passing on all plugins registed in Napari-HUB platform",
    )
    subcommand.add_argument(
        "--push-on-github",
        default=False,
        action="store_true",
        help="Perform the analysis/commit and creates pull request/issue on Github",
    )
    subcommand.set_defaults(func=autofix)

    return parser.parse_args(args)


def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "func"}
    status_code = args.func(**kwargs)
    exit(status_code)
