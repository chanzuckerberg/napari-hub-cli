import os
from pathlib import Path

import pytest

import napari_hub_cli

from .config_enum import CONFIG

RESOURCES = Path(napari_hub_cli.__file__).parent / "_tests/resources/"


@pytest.fixture
def make_pkg_dir(tmpdir, request):
    fn_arg_marker = request.node.get_closest_marker("required_configs")
    if fn_arg_marker:
        needed_configs = fn_arg_marker.args[0]
    else:
        needed_configs = CONFIG

    root_dir = tmpdir.mkdir("test-plugin-name")
    for cfg in needed_configs:
        fn = cfg.value
        if isinstance(fn, tuple):
            if not os.path.exists(os.path.join(root_dir, fn[0])):
                new_fn = root_dir.mkdir(fn[0]).join(fn[1])
                current_fn = os.path.join(RESOURCES, os.path.join(fn[0], fn[1]))
        else:
            new_fn = root_dir.join(fn)
            current_fn = os.path.join(RESOURCES, fn)
        with open(current_fn) as template:
            new_fn.write(template.read())
    return root_dir
