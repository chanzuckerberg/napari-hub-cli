from napari_hub_cli.checklist.analysis import analyse_remote_plugin
from napari_hub_cli.checklist.projectquality import project_quality_suite
from napari_hub_cli.checklist.analysis import build_csv_dict
import traceback
import csv
from pathlib import Path

FPATH = Path("batched/merged.csv")

OK_PLUGINS = [
    "Partial-Aligner",
    "napari-PICASSO",
    "napari-amdtrk",
    "napari-bil-data-viewer",
    "napari-brainbow-diagnose",
    "napari-imsmicrolink",
    "napari-lazy-openslide",
    "napari-ndtiffs",
    "napari-IDS"

]

BROKEN_PLUGINS = [
    "napari-bacseg",
    "napari-calibration",
    "napari-yolov5"
]

def load_plugins_with_errors(fpath):
    errors = []
    with open(fpath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Analysis Status"] == "Error":
                errors.append(row["Plugin Name"])

    return errors


def main(fpath, temp_dir="temp", no_pip=False):
    plugins = load_plugins_with_errors(fpath)
    print(f"Found {len(plugins)} plugins with errors")
    for plugin in plugins:
        if plugin in OK_PLUGINS:
            print(f"Skipping plugin {plugin} as it is known to be OK")
            continue
        if plugin in BROKEN_PLUGINS:
            print(f"Plugin {plugin} was known to be broken")
        print(f"Anlaysing plugin {plugin}")
        result = analyse_remote_plugin(
            plugin,
            display_info=False,
            directory=temp_dir,
            disable_pip_based_requirements=no_pip,
            requirements_suite=project_quality_suite,
        )
        print("Success")
        print(build_csv_dict({plugin: result})[0])


if __name__ == "__main__":
    main(FPATH, no_pip=True)
