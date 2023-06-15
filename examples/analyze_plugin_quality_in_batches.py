import csv
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
import time
import requests
import traceback

from napari_hub_cli.utils import get_all_napari_plugin_names
from napari_hub_cli.checklist.analysis import (
    analyse_remote_plugin,
    build_csv_dict,
    write_csv,
)
from napari_hub_cli.checklist.projectquality import project_quality_suite


def batch_plugin_names(all_plugins, batch_size=10):
    """Yield successive batch-size chunks from all_plugins."""
    for i in range(0, len(all_plugins), batch_size):
        yield all_plugins[i : i + batch_size]


def perform_batched_analysis(
    batched_names, output_dir, temp_dir="temp_dir", no_pip=False
):
    """Perform the analysis on the batched plugins"""
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    errors_filepath = Path(output_dir) / f"errors_{date}.txt"
    with open(errors_filepath, "w") as f:
        for i, plugin_names in enumerate(batched_names):
            results_dict = {}
            for plugin_name in plugin_names:
                while not ensure_github_api_rate_limit():
                    print("Github api rate limit exceeded, waiting 20 minutes")
                    time.sleep(20 * 60)
                try:
                    print(f"Analysing plugin {plugin_name}")
                    result = analyse_remote_plugin(
                        plugin_name=plugin_name,
                        display_info=False,
                        directory=temp_dir,
                        requirements_suite=project_quality_suite,
                        disable_pip_based_requirements=no_pip,
                    )
                except Exception as e:
                    print(f"Error in batch {i}, plugin {plugin_name}: {e}")
                    f.write(f"Error in batch {i}, plugin {plugin_name}: {e}\n")
                    traceback.print_exc(file=f)
                    f.write("\n"
                            "------------------------------------------------------------------\n")
                    continue
                results_dict[plugin_name] = result

            rows = build_csv_dict(results_dict)
            write_csv(rows, Path(output_dir) / f"batched_analysis_{i}.csv")


def merge_csvs(directory_with_files):
    """Merge the csv files in a directory into one csv file"""
    csv_files = Path(directory_with_files).glob("*.csv")
    with open("merged.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for csv_file in csv_files:
            with open(csv_file, newline="") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    writer.writerow(row)


def get_github_api_status():
    """Get the status of the github api"""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url)
    return response.json()


def ensure_github_api_rate_limit():
    """Ensure that the github api rate limit is not exceeded"""
    status = get_github_api_status()
    remaining = status["resources"]["core"]["remaining"]
    if remaining < 1:
        return False
    return True


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="batched_analysis",
        help="Directory to store the batched analysis csv files",
    )
    parser.add_argument(
        "--no-pip",
        "-n",
        action="store_true",
        help="Disable the pip based analysis (installability, number of dependencies, ...)",
    )
    parser.add_argument(
        "--merge-only",
        "-m",
        action="store_true",
        help="Only merge the csv files in the output directory into one csv file",
    )
    parser.add_argument(
        "--batch-size",
        "-s",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--temp-dir",
        "-t",
        type=str,
        default="temp_dir",
        help="Directory to store the temporary cloned repositories",
    )
    args = parser.parse_args()
    if args.merge_only:
        merge_csvs(args.output_dir)
        return

    all_plugins = list(get_all_napari_plugin_names())
    batched_plugins = batch_plugin_names(all_plugins, batch_size=args.batch_size)
    perform_batched_analysis(
        batched_plugins, args.output_dir, args.temp_dir, args.no_pip
    )
    merge_csvs(args.output_dir)


if __name__ == "__main__":
    main()
