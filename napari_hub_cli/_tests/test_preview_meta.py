# Test fixture for generating temp directories
    # could take any combination of 
    # .napari/DESCRIPTION.md, .napari/config.yml, setup.py, setup.cfg
# It just puts together temp directories with those files
    # our test directory will need example files
        # write some manually
import os
import pytest
from yaml import load
from .config_enum import CONFIG
from napari_hub_cli.napari_hub_cli import load_meta
from napari_hub_cli.constants import FIELDS, PROJECT_URLS

RESOURCES = './napari_hub_cli/_tests/resources/'

@pytest.fixture
def make_pkg_dir(tmpdir, request):
    fn_arg_marker = request.node.get_closest_marker("required_configs")
    if fn_arg_marker:
        needed_configs = fn_arg_marker.args[0]
    else:
        needed_configs = CONFIG

    root_dir = tmpdir.mkdir('test-plugin-name')
    for cfg in needed_configs:
        fn = cfg.value
        if isinstance(fn, tuple):
            new_fn = root_dir.mkdir(fn[0]).join(fn[1])
            current_fn = os.path.join(RESOURCES, os.path.join(fn[0], fn[1]))
        else:
            new_fn = root_dir.join(fn)
            current_fn = os.path.join(RESOURCES, fn)
        with open(current_fn) as template:
            new_fn.write(template.read())
    return root_dir

@pytest.mark.required_configs([CONFIG.YML])
def test_config_yml(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict, src_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        assert proj_url in meta_dict
        assert src_dict[proj_url] == ('/.napari/config.yml', f"project_urls, {proj_url}")

# test fixture for different version options?

# test reading yml config separately
    # containing authors
    # not containing authors
    # containing some urls but not all
    # containing different urls

# test reading setup cfg separately
    # a few combinations of simple metadata
    # all options for complex metadata

# test reading setup py separately
    # a few combinations of simple metadata
    # all options for complex metadata

# version reading should be separate

# test not overriden once set

# test source ?