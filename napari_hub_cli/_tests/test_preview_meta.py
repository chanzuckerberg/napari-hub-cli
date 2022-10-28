import os

import pytest

from napari_hub_cli.constants import DESC_LENGTH, FIELDS, PROJECT_URLS
from napari_hub_cli.meta_classes import MetaItem
from napari_hub_cli.napari_hub_cli import load_meta
from napari_hub_cli.utils import get_github_license

from .config_enum import CONFIG

DEMO_GITHUB_REPO = "https://github.com/DragaDoncila/example-plugin"


@pytest.mark.required_configs([CONFIG.YML])
def test_config_yml(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        f_pth, section, key = meta_dict[proj_url].source.unpack()
        assert f_pth == ".napari/config.yml"
        assert section == "project_urls"
        assert key == proj_url

    # assert other urls are not included
    assert "Other Link" not in meta_dict

    # authors have been read correctly
    assert "Authors" in meta_dict
    assert isinstance(meta_dict["Authors"].value, list)
    assert meta_dict["Authors"].value[0]["name"] == "Jane Doe"
    assert len(meta_dict["Authors"].value) == 2
    f_pth, section, key = meta_dict["Authors"].source.unpack()
    assert f_pth == ".napari/config.yml"
    assert section == "authors"
    assert key is None


@pytest.mark.required_configs([CONFIG.YML, CONFIG.CFG])
def test_config_yml_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    for proj_url in PROJECT_URLS:
        # all project urls have been read and are sourced from config yml
        assert proj_url in meta_dict
        f_pth, section, key = meta_dict[proj_url].source.unpack()
        assert f_pth == ".napari/config.yml"
        assert section == "project_urls"
        assert key == proj_url

    # assert other urls are not included
    assert "Other Link" not in meta_dict

    # authors have been read correctly
    assert "Authors" in meta_dict


@pytest.mark.required_configs([CONFIG.DESC, CONFIG.CFG, CONFIG.README])
def test_description_not_overriden(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    assert meta_dict["Description"].value == "Test .napari Description."
    f_pth, section, key = meta_dict["Description"].source.unpack()
    assert f_pth == ".napari/DESCRIPTION.md"
    assert section is None
    assert key is None


@pytest.mark.required_configs([CONFIG.CFG, CONFIG.README])
def test_cfg_description(make_pkg_dir):
    root_dir = make_pkg_dir
    meta_dict = load_meta(root_dir)

    assert meta_dict["Description"].value == "Test README Description."
    f_pth, section, key = meta_dict["Description"].source.unpack()
    assert f_pth == "setup.cfg"
    assert section == "metadata"
    assert key == "long_description"


@pytest.mark.required_configs([CONFIG.INIT])
def test_version_init_setup_cfg(make_pkg_dir):
    root_dir = make_pkg_dir
    stup = root_dir / "setup.cfg"
    stup.write_text("[metadata]\nname = test-plugin-name")

    meta = load_meta(root_dir)

    assert isinstance(meta["Version"], MetaItem)
    assert meta["Version"].value == "0.0.1"
    f_pth, _, _ = meta["Version"].source.unpack()
    assert os.path.basename(str(f_pth)) == "__init__.py"


@pytest.mark.required_configs([CONFIG.INIT])
def test_version_init_setup_py(make_pkg_dir):
    root_dir = make_pkg_dir
    stup = root_dir / "setup.py"
    stup.write_text("from setuptools import setup\nsetup()")

    meta = load_meta(root_dir)

    assert isinstance(meta["Version"], MetaItem)
    assert meta["Version"].value == "0.0.1"
    f_pth, _, _ = meta["Version"].source.unpack()
    assert os.path.basename(str(f_pth)) == "__init__.py"


@pytest.mark.required_configs([CONFIG.SCM_VERS])
def test_version_scm(make_pkg_dir):
    root_dir = make_pkg_dir
    stup = root_dir / "setup.py"
    stup.write_text("from setuptools import setup\nsetup()")

    meta = load_meta(root_dir)

    assert isinstance(meta["Version"], MetaItem)
    assert meta["Version"].value == "0.0.1"
    f_pth, _, _ = meta["Version"].source.unpack()
    assert os.path.basename(str(f_pth)) == "_version.py"


@pytest.mark.required_configs([CONFIG.VERS])
def test_version_file(make_pkg_dir):
    root_dir = make_pkg_dir
    stup = root_dir / "setup.py"
    stup.write_text("from setuptools import setup\nsetup()")

    meta = load_meta(root_dir)

    assert isinstance(meta["Version"], MetaItem)
    assert meta["Version"].value == "0.0.1"
    f_pth, _, _ = meta["Version"].source.unpack()
    assert os.path.basename(str(f_pth)) == "VERSION"


@pytest.mark.required_configs([CONFIG.DESC, CONFIG.YML, CONFIG.CFG])
def test_only_known_fields(make_pkg_dir):
    root_dir = make_pkg_dir
    meta = load_meta(root_dir)

    for field in meta:
        assert field in FIELDS


@pytest.mark.required_configs([CONFIG.YML, CONFIG.CFG, CONFIG.README])
def test_fields_have_source(make_pkg_dir):
    root_dir = make_pkg_dir
    meta = load_meta(root_dir)

    for field in meta:
        assert meta[field].source is not None


@pytest.mark.required_configs([CONFIG.CFG])
def test_long_description_trimmed(make_pkg_dir):
    root_dir = make_pkg_dir
    long_desc = "*" * DESC_LENGTH * 2
    readme = root_dir / "README.md"
    readme.write_text(long_desc)

    meta = load_meta(root_dir)
    # trimmed description plus the dots
    assert len(meta["Description"].value) == DESC_LENGTH + 3

    # same for DESCRIPTION.md
    napari_dir = root_dir / ".napari"
    napari_dir.mkdir()
    desc = napari_dir / "DESCRIPTION.md"
    desc.write_text(long_desc)
    meta = load_meta(root_dir)
    assert meta["Description"].source.src_file == ".napari/DESCRIPTION.md"
    assert len(meta["Description"].value) == DESC_LENGTH + 3


def test_long_description_cfg(tmp_path):
    root_dir = tmp_path / "test-long-description"
    root_dir.mkdir()
    setup_cfg_file = root_dir / "setup.cfg"
    setup_cfg_file.write_text(
        f"""
[metadata]
name = test-plugin-name
long_description = {'*' * DESC_LENGTH*2}
    """
    )

    meta = load_meta(f"{root_dir}")
    assert "Description" in meta
    assert len(meta["Description"].value) == DESC_LENGTH + 3


def test_setup_py_proj_urls(tmp_path):
    root_dir = tmp_path / "test-setup-py-proj-urls"
    root_dir.mkdir()
    setup_py_file = root_dir / "setup.py"
    proj_site = "https://test-plugin-name.com"
    twitter = "https://twitter.com/test-plugin-name"
    bug_tracker = "https://github.com/user/test-plugin-name"

    setup_py_file.write_text(
        f"""
from setuptools import setup

setup(
    name = 'test-plugin-name',
    url = '{proj_site}',
    project_urls = {{
        'Twitter': '{twitter}',
        'Bug Tracker': '{bug_tracker}'
        }}
)
    """
    )
    meta = load_meta(f"{root_dir}")
    for key, value in zip(
        ["Project Site", "Bug Tracker", "Twitter"], [proj_site, bug_tracker, twitter]
    ):
        assert key in meta
        assert meta[key].value == value


def test_setup_cfg_proj_urls(tmp_path):
    root_dir = tmp_path / "test-setup-cfg-proj-urls"
    root_dir.mkdir()
    setup_cfg_file = root_dir / "setup.cfg"
    proj_site = "https://test-plugin-name.com"
    twitter = "https://twitter.com/test-plugin-name"
    bug_tracker = "https://github.com/user/test-plugin-name"

    setup_cfg_file.write_text(
        f"""
[metadata]
url = {proj_site}
project_urls =
    Bug Tracker = {bug_tracker}
    Twitter = {twitter}
    """
    )
    meta = load_meta(f"{root_dir}")
    for key, value in zip(
        ["Project Site", "Bug Tracker", "Twitter"], [proj_site, bug_tracker, twitter]
    ):
        assert key in meta
        assert meta[key].value == value


def test_source_code_url(tmp_path):
    root_dir = tmp_path / "test-source-code-url"
    root_dir.mkdir()
    setup_py_file = root_dir / "setup.py"
    proj_site = "https://github.com/user/test-plugin-name"

    setup_py_file.write_text(
        f"""
from setuptools import setup

setup(
    name = 'test-plugin-name',
    url = '{proj_site}'
)
    """
    )

    meta = load_meta(f"{root_dir}")
    assert "Project Site" not in meta
    assert "Source Code" in meta
    assert meta["Source Code"].value == proj_site


def test_github_license():
    meta = {}
    meta["Source Code"] = MetaItem("Source Code", DEMO_GITHUB_REPO)

    github_api_license = get_github_license(meta)
    assert github_api_license == "BSD-3-Clause"


def test_github_license_overrides_local(tmp_path):
    root_dir = tmp_path / "test-github-license-overrides-local"
    root_dir.mkdir()
    setup_cfg_file = root_dir / "setup.cfg"

    setup_cfg_file.write_text(
        f"""
[metadata]
license = MIT
project_urls =
    Source Code = {DEMO_GITHUB_REPO}
"""
    )
    meta = load_meta(f"{root_dir}")
    assert "License" in meta
    license_src = meta["License"].source
    assert license_src.src_file == "GitHub Repository"
    assert meta["License"].value == "BSD-3-Clause"
