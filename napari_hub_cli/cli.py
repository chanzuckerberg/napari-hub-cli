"""Console script for napari_hub_cli."""
import argparse
import sys
from .napari_hub_cli import load_meta, format_meta, print_meta_interactive
import os


def preview_meta(args):
    pth = args.plugin_path
    if not os.path.exists(pth):
        print(f"Nothing found at path: {pth}")
    else:
        meta = load_meta(pth)
        if len(meta) == 0 or len(meta) == 1 and "Version" in meta:
            print(f"Found no metadata. Is {pth} the root of a python package?")
        else:
            if args.i:
                print_meta_interactive(meta)
            else:
                formatted_meta = format_meta(meta)
                print(formatted_meta)


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
    return parser.parse_args(args)


def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""
    args = parse_args(argv)
    args.func(args)

    return 0
