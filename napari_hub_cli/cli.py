"""Console script for napari_hub_cli."""
import argparse
import sys
from .napari_hub_cli import load_meta, format_meta
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
            formatted_meta = format_meta(meta)
            print(formatted_meta)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_preview_metadata = subparsers.add_parser("preview-metadata")
parser_preview_metadata.add_argument("plugin_path", help="Local path to your plugin")
parser_preview_metadata.set_defaults(func=preview_meta)


def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""
    args = parser.parse_args(argv)
    args.func(args)

    return 0
