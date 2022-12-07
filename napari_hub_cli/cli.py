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
from .checklist.analysis import (
    analyze_all_remote_plugins,
    build_csv_dict,
    display_remote_analysis,
    write_csv,
)
from .checklist.metadata_checklist import create_checklist, display_checklist
from .citations.citation import create_cff_citation
from .formatting import (
    format_meta,
    format_missing,
    print_meta_interactive,
    print_missing_interactive,
)
from .napari_hub_cli import get_missing, load_meta
from .utils import get_all_napari_plugin_names


def preview_meta(plugin_path, i):
    """Takes args.plugin_path and prints current and missing metadata

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
        return 1  # code 1 is for unknown path
    meta = load_meta(plugin_path)
    if len(meta) == 0 or len(meta) == 1 and "Version" in meta:
        print(f"Found no metadata. Is {plugin_path} the root of a Python package?")
        return 2  # code 2 is for missing metadata
    missing_meta = get_missing(meta, plugin_path)
    if i:
        print_meta_interactive(meta, missing_meta)
    else:
        formatted_meta = format_meta(meta, missing_meta)
        print(formatted_meta)
    return 0  # code 0 is for all went good


def check_missing(plugin_path, i):
    """Check and print missing metadata for plugin at args.plugin_path

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
    meta = load_meta(plugin_path)
    if len(meta) == 0 or len(meta) == 1 and "Version" in meta:
        print(f"Found no metadata. Is {plugin_path} the root of a Python package?")
        return 2
    missing_meta = get_missing(meta, plugin_path)
    if i:
        print_missing_interactive(missing_meta)
        return 0
    formatted_missing = format_missing(missing_meta)
    print(formatted_missing)
    return 0


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


def documentation_checklist(plugin_path, i):
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
    check_list = create_checklist(plugin_path)
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

    parser_preview_metadata = subparsers.add_parser("preview-metadata")
    parser_preview_metadata.add_argument(
        "plugin_path", help="Local path to your plugin"
    )
    parser_preview_metadata.set_defaults(func=preview_meta)
    parser_preview_metadata.add_argument(
        "-i",
        default=False,
        action="store_true",
        help="Wait for user input after each field",
    )

    parser_check_missing = subparsers.add_parser("check-missing")
    parser_check_missing.add_argument("plugin_path", help="Local path to your plugin")
    parser_check_missing.add_argument(
        "-i",
        default=False,
        action="store_true",
        help="Wait for user input after each field",
    )
    parser_check_missing.set_defaults(func=check_missing)

    parser_doc_checklist = subparsers.add_parser(
        "create-doc-checklist", help="Checks consistency of a local plugin"
    )
    parser_doc_checklist.add_argument("plugin_path", help="Local path to your plugin")
    parser_doc_checklist.add_argument(
        "-i",
        default=False,
        action="store_true",
        help="Wait for user input after each field",
    )
    parser_doc_checklist.set_defaults(func=documentation_checklist)

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
    subcommand = subparsers.add_parser("create-cff-citation")
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
