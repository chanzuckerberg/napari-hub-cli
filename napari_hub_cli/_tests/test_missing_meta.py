import pytest
from .config_enum import CONFIG
from napari_hub_cli.napari_hub_cli import get_missing, load_meta
from napari_hub_cli.constants import FIELDS, PROJECT_URLS, YML_META


def assert_cfg_src(meta, missing):
    for field in FIELDS:
        if field != "Version" and field not in meta:
            assert field in missing
            if field != "Description" and field not in YML_META:
                assert missing[field].src_file == "/setup.cfg"


def test_suggested_src_cfg(tmpdir):
    """Test when cfg exists, we suggest cfg as source"""
    root_dir = tmpdir.mkdir("test-plugin-name")
    setup_cfg_file = root_dir.join("setup.cfg")
    setup_cfg_file.write(
        f"""
[metadata]
name = test-plugin-name
    """
    )

    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)

    assert_cfg_src(meta, missing)


@pytest.mark.required_configs([CONFIG.YML])
def test_no_setup_suggest_cfg(make_pkg_dir):
    root_dir = make_pkg_dir

    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)

    assert_cfg_src(meta, missing)


@pytest.mark.required_configs([CONFIG.CFG, CONFIG.PY, CONFIG.README])
def test_both_setup_suggest_cfg(make_pkg_dir):
    root_dir = make_pkg_dir

    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)

    assert_cfg_src(meta, missing)


def test_setup_py_no_cfg_suggest_py(tmpdir):
    root_dir = tmpdir.mkdir("test-plugin-name")
    setup_py_file = root_dir.join("setup.py")

    setup_py_file.write(
        f"""
from setuptools import setup

setup(
    name = 'test-plugin-name',
)
    """
    )
    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)
    for field in FIELDS:
        if field not in meta:
            assert field in missing
            if field != "Description" and field not in YML_META:
                assert missing[field].src_file == "/setup.py"


def test_no_missing_in_full_config(make_pkg_dir):
    root_dir = make_pkg_dir
    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)

    assert len(missing) == 0


@pytest.mark.required_configs([CONFIG.YML])
def test_description_src(make_pkg_dir):
    root_dir = make_pkg_dir
    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)

    assert "Description" in missing
    file_pth, _, _ = missing["Description"].unpack()
    assert file_pth == "/.napari/DESCRIPTION.md"


@pytest.mark.required_configs([CONFIG.CFG])
def test_proj_urls_src(make_pkg_dir):
    root_dir = make_pkg_dir
    meta = load_meta(root_dir)
    missing = get_missing(meta, root_dir)
    f_pth = "/.napari/config.yml"
    section = "project_urls"

    for url in PROJECT_URLS:
        if url not in meta:
            assert url in missing
            assert (f_pth, section, url) == missing[url].unpack()
