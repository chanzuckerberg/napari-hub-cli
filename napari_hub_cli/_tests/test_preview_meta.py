import os
import pytest
from yaml import load
from .config_enum import CONFIG
from napari_hub_cli.napari_hub_cli import load_meta
from napari_hub_cli.constants import FIELDS, PROJECT_URLS

RESOURCES = "./napari_hub_cli/_tests/resources/"


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
    meta_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        f_pth, section, key = meta_dict[proj_url].source.unpack()
        assert f_pth == "/.napari/config.yml"
        assert section == "project_urls"
        assert key == proj_url

    # assert other urls are not included
    assert "Other Link" not in meta_dict

    # authors have been read correctly
    assert "Authors" in meta_dict
    assert isinstance(meta_dict["Authors"].value, list)
    assert len(meta_dict["Authors"].value) == 2


@pytest.mark.required_configs([CONFIG.YML, CONFIG.CFG, CONFIG.README])
def test_config_yml_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        f_pth, section, key = meta_dict[proj_url].source.unpack()
        assert f_pth == "/.napari/config.yml"
        assert section == "project_urls"
        assert key == proj_url

    # assert other urls are not included
    assert "Other Link" not in meta_dict

    # authors have been read correctly
    assert "Authors" in meta_dict
    f_pth, section, key = meta_dict["Authors"].source.unpack()
    assert f_pth == "/.napari/config.yml"
    assert section == "authors"
    assert key is None


@pytest.mark.required_configs([CONFIG.DESC, CONFIG.CFG, CONFIG.README])
def test_description_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    assert meta_dict["Description"].value == "Test .napari Description."
    f_pth, section, key = meta_dict["Description"].source.unpack()
    assert f_pth == "/.napari/DESCRIPTION.md"
    assert section is None
    assert key is None


@pytest.mark.required_configs([CONFIG.CFG, CONFIG.README])
def test_cfg_description(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    assert meta_dict["Description"].value == "Test README Description."
    f_pth, section, key = meta_dict["Description"].source.unpack()
    assert f_pth == "/setup.cfg"
    assert section == "metadata"
    assert key == "long_description"


# when we want 'custom' templates, we can make them ourselves based on some template files

# test reading setup cfg separately
# a few combinations of simple metadata
# all options for complex metadata

# test reading setup py separately
# a few combinations of simple metadata
# all options for complex metadata

# version reading should be separate

# test source ?
