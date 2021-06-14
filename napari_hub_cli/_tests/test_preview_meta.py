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
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        assert src_dict[proj_url] == ('/.napari/config.yml', f"project_urls, {proj_url}")

    # assert other urls are not included
    assert 'Other Link' not in meta_dict

    # authors have been read correctly
    assert 'Authors' in meta_dict
    assert isinstance(meta_dict['Authors'], list)
    assert len(meta_dict['Authors']) == 2

@pytest.mark.required_configs([CONFIG.YML, CONFIG.CFG, CONFIG.README])
def test_config_yml_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict, src_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        assert src_dict[proj_url] == ('/.napari/config.yml', f"project_urls, {proj_url}")

    # assert other urls are not included
    assert 'Other Link' not in meta_dict

    # authors have been read correctly
    assert 'Authors' in meta_dict
    assert src_dict['Authors'] == ('/.napari/config.yml', f"authors")

@pytest.mark.required_configs([CONFIG.DESC, CONFIG.CFG, CONFIG.README])
def test_description_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict, src_dict = load_meta(root_dir)

    assert meta_dict["Description"] == "Test .napari Description."
    assert src_dict["Description"] == ('/.napari/DESCRIPTION.md', None)

@pytest.mark.required_configs([CONFIG.CFG, CONFIG.README])
def test_cfg_description(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict, src_dict = load_meta(root_dir)
    
    assert meta_dict["Description"] == 'Test README Description.'
    assert src_dict["Description"] == ('/setup.cfg', 'metadata, long_description')
# when we want 'custom' templates, we can make them ourselves based on some template files

# test reading setup cfg separately
    # a few combinations of simple metadata
    # all options for complex metadata

# test reading setup py separately
    # a few combinations of simple metadata
    # all options for complex metadata

# version reading should be separate

# test source ?