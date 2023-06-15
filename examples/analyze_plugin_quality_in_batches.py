import csv
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
import time
import requests
import traceback
import multiprocessing

from napari_hub_cli.utils import get_all_napari_plugin_names
from napari_hub_cli.checklist.analysis import (
    analyse_remote_plugin,
    build_csv_dict,
    write_csv,
)
from napari_hub_cli.checklist.projectquality import project_quality_suite


def batch_wrapper(plugin_name, temp_dir, no_pip, result_queue):
    try:
        print(f"Analysing plugin {plugin_name}")
        result = analyse_remote_plugin(
            plugin_name=plugin_name,
            display_info=False,
            directory=temp_dir,
            requirements_suite=project_quality_suite,
            disable_pip_based_requirements=no_pip,
        )
        result_queue.put(result)
    except Exception as e:
        result_queue.put(e)
    return result


def batch_plugin_names(all_plugins, batch_size=10):
    """Yield successive batch-size chunks from all_plugins."""
    for i in range(0, len(all_plugins), batch_size):
        yield all_plugins[i : i + batch_size]


def find_aleady_analysed_plugins(output_dir):
    """Find the plugins that have already been analysed"""
    csv_files = Path(output_dir).glob("*.csv")
    analysed_plugins = set()
    for csv_file in csv_files:
        with open(csv_file, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                analysed_plugins.add(row[0])
    return analysed_plugins


def perform_batched_analysis(
    batched_names,
    output_dir,
    temp_dir="temp_dir",
    no_pip=False,
    overwrite=False,
    timeout=180,
):
    """Perform the analysis on the batched plugins"""
    if not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    errors_filepath = Path(output_dir) / f"errors_{date}.txt"
    analysed = find_aleady_analysed_plugins(output_dir)
    for i, plugin_names in enumerate(batched_names):
        results_dict = {}
        for plugin_name in plugin_names:
            if plugin_name in analysed and not overwrite:
                print(
                    f"Skipping plugin {plugin_name} as it has already been analysed"
                )
                continue
            while not ensure_github_api_rate_limit():
                print("Github api rate limit exceeded, waiting 20 minutes")
                time.sleep(20 * 60)
            result_queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=batch_wrapper,
                args=(plugin_name, temp_dir, no_pip, result_queue),
            )
            process.start()
            process.join(timeout)
            if process.is_alive():
                process.terminate()
                process.join()
            result = result_queue.get()
            if isinstance(result, Exception):
                with open(errors_filepath, "a") as f:
                    print(f"Plugin {plugin_name} failed with error {result}")
                    f.write(f"Plugin {plugin_name} failed with error {result}\n")
                    f.write(traceback.format_exc())
                    f.write("\n------------------\n")
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
    parser.add_argument(
        "--overwrite",
        "-w",
        action="store_true",
        help="Overwrite existing csv files in the output directory",
    )
    parser.add_argument(
        "--timeout",
        "-to",
        type=int,
        default=180,
        help="Timeout in seconds for each plugin analysis",
    )
    args = parser.parse_args()
    if args.merge_only:
        merge_csvs(args.output_dir)
        return

    all_plugins = list(get_all_napari_plugin_names())
    batched_plugins = batch_plugin_names(all_plugins, batch_size=args.batch_size)
    perform_batched_analysis(
        batched_plugins,
        args.output_dir,
        args.temp_dir,
        args.no_pip,
        args.overwrite,
        args.timeout,
    )
    merge_csvs(args.output_dir)


if __name__ == "__main__":
    main()
