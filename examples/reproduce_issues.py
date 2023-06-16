from napari_hub_cli.checklist.analysis import analyse_remote_plugin
from napari_hub_cli.checklist.projectquality import project_quality_suite
from napari_hub_cli.checklist.analysis import build_csv_dict
import traceback

PLUGINS = ["napari-LF", "napari-cookiecut", "elastix-napari", "disease-classifier"]


def main(plugins, temp_dir="temp", no_pip=False):
    for plugin in plugins:
        print(f"Anlaysing plugin {plugin}")
        try:
            result = analyse_remote_plugin(
                plugin,
                display_info=False,
                directory=temp_dir,
                disable_pip_based_requirements=no_pip,
                requirements_suite=project_quality_suite,
            )
        except Exception as e:
            print(f"Error analysing plugin {plugin}: {e}")
            traceback.print_exc()
            continue
        else:
            print("Success")
            print(build_csv_dict({plugin: result})[0])


if __name__ == "__main__":
    main(PLUGINS)
