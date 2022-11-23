import shutil
from pathlib import Path

import pytest

from napari_hub_cli.fs import ConfigFile, NapariPlugin
from napari_hub_cli.fs.configfiles import (
    NapariConfig,
    Npe2Yaml,
    PyProjectToml,
    SetupCfg,
    SetupPy,
)
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


def test_napari_plugin_dir_delete():
    with TemporaryDirectory(delete=False) as dirname:
        p = Path(dirname)
        plugin_repo = NapariPlugin(p)
        assert p.exists() is True
        assert plugin_repo.exists is True
    assert p.exists() is True
    assert plugin_repo.exists is True

    plugin_repo.delete()
    assert p.exists() is False
    assert plugin_repo.exists is False

    with pytest.raises(FileNotFoundError):
        plugin_repo.delete()


def test_screenshot_detection(resources):
    readme = MarkdownDescription.from_file(resources / "README.md")

    assert readme.has_screenshots is True
    assert readme.has_videos is False
    assert readme.has_videos_or_screenshots is True


@pytest.fixture
def file(tmp_path, filename):
    file = tmp_path / filename
    return file


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.cfg", "name", "NAME1"),
        ("s1.cfg", "author", "Jane Doe"),
        ("s1.cfg", "sourcecode", "https://repo"),
        ("s1.cfg", "bugtracker", "https://repo/bt"),
        ("s1.cfg", "usersupport", "https://repo/us"),
        ("s1.cfg", "summary", "This is a summary"),
    ],
)
def test_memwrite_read_cfg(file, key, value):
    config = SetupCfg(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.cfg", "name", "NAME1"),
        ("s1.cfg", "author", "Jane Doe"),
        ("s1.cfg", "sourcecode", "https://repo"),
        ("s1.cfg", "bugtracker", "https://repo/bt"),
        ("s1.cfg", "usersupport", "https://repo/us"),
        ("s1.cfg", "summary", "This is a summary"),
    ],
)
def test_write_read_cfg(file, key, value):
    config = SetupCfg(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value

    config.save()
    config = SetupCfg(file)  # force reload file
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value, equivalent",
    [
        ("s1.toml", "name", "NAME1", "NAME1"),
        ("s1.toml", "author", "Jane Doe", ["Jane Doe"]),
        ("s1.toml", "sourcecode", "https://repo", "https://repo"),
        ("s1.toml", "bugtracker", "https://repo/bt", "https://repo/bt"),
        ("s1.toml", "usersupport", "https://repo/us", "https://repo/us"),
        ("s1.toml", "summary", "This is a summary", "This is a summary"),
    ],
)
def test_memwrite_read_toml(file, key, value, equivalent):
    config = PyProjectToml(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == equivalent


@pytest.mark.parametrize(
    "filename, key, value, equivalent",
    [
        ("s1.toml", "name", "NAME1", "NAME1"),
        ("s1.toml", "author", "Jane Doe", ["Jane Doe"]),
        ("s1.toml", "sourcecode", "https://repo", "https://repo"),
        ("s1.toml", "bugtracker", "https://repo/bt", "https://repo/bt"),
        ("s1.toml", "usersupport", "https://repo/us", "https://repo/us"),
        ("s1.toml", "summary", "This is a summary", "This is a summary"),
    ],
)
def test_write_read_toml(file, key, value, equivalent):
    config = PyProjectToml(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == equivalent

    config.save()
    config = PyProjectToml(file)  # force reload file
    assert getattr(config, key) == equivalent


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.yml", "summary", "This is a summary"),
    ],
)
def test_memwrite_read_napari_config(file, key, value):
    config = NapariConfig(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.yml", "summary", "This is a summary"),
    ],
)
def test_write_read_napari_config(file, key, value):
    config = NapariConfig(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value

    config.save()
    config = NapariConfig(file)  # force reload file
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.py", "name", "NAME1"),
        ("s1.py", "author", "Jane Doe"),
        ("s1.py", "sourcecode", "https://repo"),
        ("s1.py", "bugtracker", "https://repo/bt"),
        ("s1.py", "usersupport", "https://repo/us"),
        ("s1.py", "summary", "This is a summary"),
    ],
)
def test_memwrite_read_py(file, key, value):
    config = SetupPy(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.py", "name", "NAME1"),
        ("s1.py", "author", "Jane Doe"),
        ("s1.py", "sourcecode", "https://repo"),
        ("s1.py", "bugtracker", "https://repo/bt"),
        ("s1.py", "usersupport", "https://repo/us"),
        ("s1.py", "summary", "This is a summary"),
    ],
)
def test_write_read_py(file, key, value):
    config = SetupPy(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value

    assert config.save() is False
    config = SetupPy(file)  # force reload file
    assert getattr(config, key) is None


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.yml", "name", "Jane Doe"),
    ],
)
def test_memwrite_read_napari_yml(file, key, value):
    config = Npe2Yaml(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value


@pytest.mark.parametrize(
    "filename, key, value",
    [
        ("s1.yml", "name", "Jane Doe"),
    ],
)
def test_write_read_napari_yml(file, key, value):
    config = Npe2Yaml(file)
    assert getattr(config, key) is None

    setattr(config, key, value)
    assert getattr(config, key) == value

    config.save()
    config = Npe2Yaml(file)  # force reload file
    assert getattr(config, key) == value


def test_complete_cfg(resources):
    cfg_file = resources / "complete_setup.cfg"
    cfg = SetupCfg(cfg_file)

    assert cfg.has_name is True
    assert cfg.name == "napari_plot"
    assert cfg.has_author is True
    assert cfg.author == "Lukasz G. Migas"
    assert cfg.has_summary is True
    assert cfg.summary == "Plugin providing support for 1d plotting in napari."
    assert cfg.has_bugtracker is True
    assert cfg.bugtracker == "https://github.com/lukasz-migas/napari-1d/issues"
    assert cfg.has_sourcecode is True
    assert cfg.sourcecode == "https://github.com/lukasz-migas/napari-1d"
    assert cfg.has_usersupport is True
    assert cfg.usersupport == "https://github.com/lukasz-migas/napari-1d/issues"
