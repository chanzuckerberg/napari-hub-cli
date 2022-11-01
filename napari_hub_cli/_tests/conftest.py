from pathlib import Path

import pytest
import requests_mock

import napari_hub_cli

from .config_enum import CONFIG, DEMO_GITHUB_REPO

RESOURCES = Path(napari_hub_cli.__file__).parent / "_tests/resources/"
MOCK_REQUESTS = None


def pytest_addoption(parser):
    parser.addoption(
        "--online",
        action="store_true",
        default=False,
        help="runs tests with an internet access for requests",
    )


def pytest_configure(config):
    if config.getoption("--online"):
        return
    global MOCK_REQUESTS
    MOCK_REQUESTS = requests_mock.Mocker()  # general mock
    MOCK_REQUESTS.start()
    # mock everything to an empty json
    MOCK_REQUESTS.register_uri("GET", requests_mock.ANY, json={})
    # mock calls to the demo repository
    with open(RESOURCES / "license.json", "r", encoding="utf-8") as license:
        repository_url = DEMO_GITHUB_REPO
        api_url = repository_url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        )
        MOCK_REQUESTS.register_uri("GET", f"{api_url}/license", text=license.read())


def pytest_unconfigure(config):
    if MOCK_REQUESTS is not None:
        MOCK_REQUESTS.stop()


@pytest.fixture
def make_pkg_dir(tmp_path, request):
    fn_arg_marker = request.node.get_closest_marker("required_configs")
    if fn_arg_marker:
        needed_configs = fn_arg_marker.args[0]
    else:
        needed_configs = CONFIG

    root_dir = tmp_path / "test-plugin-name"
    root_dir.mkdir()
    for cfg in needed_configs:
        fn = cfg.value
        if isinstance(fn, tuple):
            new_dir = root_dir / fn[0]
            new_dir.mkdir(exist_ok=True)
            new_fn = new_dir / fn[1]
            current_fn = RESOURCES / Path(fn[0]) / Path(fn[1])
        else:
            new_fn = root_dir / fn
            current_fn = RESOURCES / fn
        with open(current_fn, "r") as template:
            new_fn.write_text(template.read())
    return root_dir
