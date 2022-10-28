from pathlib import Path

import pytest

import napari_hub_cli

from .config_enum import CONFIG

RESOURCES = Path(napari_hub_cli.__file__).parent / "_tests/resources/"


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
