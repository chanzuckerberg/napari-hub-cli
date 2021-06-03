"""Console script for napari_hub_cli."""
import argparse
import sys
from .napari_hub_cli import load_meta, format_meta

def preview_meta(args):
    pth = args.plugin_path
    meta = load_meta(pth)
    formatted_meta = format_meta(meta)
    print(f"Previewing Metadata of {pth}")

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_preview_metadata = subparsers.add_parser('preview-metadata')
parser_preview_metadata.add_argument(
    'plugin_path',
    help='Local path to your plugin'
)
parser_preview_metadata.set_defaults(
    func=preview_meta
)

def main(argv=sys.argv[1:]):
    """Console script for napari_hub_cli."""    
    args = parser.parse_args(argv)
    args.func(args)
    
    return 0
