import shutil
from pathlib import Path

import pytest

from napari_hub_cli.fs import ConfigFile
from napari_hub_cli.fs.configfiles import PyProjectToml, SetupCfg, SetupPy
from napari_hub_cli.fs.descriptions import MarkdownDescription
from napari_hub_cli.utils import TemporaryDirectory


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

    assert file.find_npe2() is not None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content == ""


def test_pyproject_toml(resources):
    content = resources / "pyproject.toml"
    file = PyProjectToml(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is False
    assert file.has_bugtracker is False
    assert file.has_summary is False

    assert file.find_npe2() is not None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""


def test_pyproject2_toml(resources):
    content = resources / "pyproject2.toml"
    file = PyProjectToml(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is False
    assert file.has_bugtracker is False
    assert file.has_summary is False

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""


def test_pyproject3_toml(resources):
    content = resources / "pyproject3.toml"
    file = PyProjectToml(content)

    assert file.file is content
    assert file.data != {}
    assert file.is_valid is True
    assert file.exists is True

    assert file.has_name is True
    assert file.has_author is False
    assert file.has_bugtracker is False
    assert file.has_summary is False

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""


def test_markdown_non_existingfile(resources):
    content = resources / "nonexisting.md"
    file = MarkdownDescription.from_file(content)

    assert file.exists is False
    assert file.raw_content == ""


def test_new_tempdir():
    with TemporaryDirectory() as dirname:
        p = Path(dirname)
        assert p.exists() is True
    assert p.exists() is False

    with TemporaryDirectory(delete=True) as dirname:
        p = Path(dirname)
        assert p.exists() is True
    assert p.exists() is False

    with TemporaryDirectory(delete=False) as dirname:
        p = Path(dirname)
        assert p.exists() is True
    assert p.exists() is True

    shutil.rmtree(f"{p.absolute()}", ignore_errors=False)
    assert p.exists() is False


def test_screenshot_detection(resources):
    readme = MarkdownDescription.from_file(resources / "README.md")

    assert readme.has_screenshots is True
    assert readme.has_videos is False
    assert readme.has_videos_or_screenshots is True
