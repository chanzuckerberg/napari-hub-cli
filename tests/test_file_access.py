import pytest
from pathlib import Path
from napari_hub_cli.documentation_checklist.filesaccess import (
    ConfigFile,
    SetupCfg,
    SetupPy,
)


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources"


def test_empty_yaml(resources):
    yml = resources / "empty_yaml.yml"
    file = ConfigFile(yml)

    assert file.file is yml
    assert file.data == {}
    assert file.is_valid is True
    assert file.exists is True


def test_setup_py(resources):
    content = resources / "setup.py"
    file = SetupPy(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is None


def test_setup2_py(resources):
    content = resources / "setup2.py"
    file = SetupPy(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is not None
    assert file.find_npe2() == resources / "module_path" / "napari.yaml"


def test_setup3_py(resources):
    content = resources / "setup3.py"
    file = SetupPy(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is None


def test_setup_cfg(resources):
    content = resources / "setup.cfg"
    file = SetupCfg(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""


def test_setup2_cfg(resources):
    content = resources / "setup2.cfg"
    file = SetupCfg(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content == ""


def test_setup3_cfg(resources):
    content = resources / "setup3.cfg"
    file = SetupCfg(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is True
    assert file.has_bugtracker is False
    assert file.has_summary is True

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content == ""
