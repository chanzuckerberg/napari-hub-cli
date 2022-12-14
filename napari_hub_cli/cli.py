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

    ## create-cff-citation
    subcommand = subparsers.add_parser("create-cff-citation")
    subcommand.add_argument("plugin_path", help="Local path to your plugin")
    subcommand.set_defaults(func=create_citation)

    return parser.parse_args(args)


def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""
    args = parse_args(argv)
    kwargs = {k: v for k, v in vars(args).items() if k != "func"}
    status_code = args.func(**kwargs)
    exit(status_code)
