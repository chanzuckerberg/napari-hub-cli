from pathlib import Path

import pytest

from napari_hub_cli.dependencies_solver.utils import LINUX, MACOS, WIN32, WIN64
from napari_hub_cli.fs import ConfigFile, NapariPlugin
from napari_hub_cli.fs.configfiles import (
    NapariConfig,
    Npe2Yaml,
    PyProjectToml,
    SetupCfg,
    SetupPy,
)
from napari_hub_cli.fs.descriptions import MarkdownDescription
from napari_hub_cli.utils import TemporaryDirectory, delete_file_tree


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

    assert file.has_version is True
    assert file.version == "0.0.1"

    assert file.find_npe2() is None

    assert file.classifiers
    assert len(file.classifiers) == 11
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert len(file.requirements) == 2
    assert "napari-plugin-engine>=0.1.4" in file.requirements
    assert "numpy" in file.requirements


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

    assert file.has_version is False
    assert file.version is None

    assert file.find_npe2() is not None
    assert file.find_npe2() == resources / "module_path" / "napari.yaml"

    assert file.classifiers == []
    assert file.requirements == []


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

    assert file.has_version is True
    assert file.version == "1.0.1"

    assert file.find_npe2() is None

    assert file.classifiers
    assert len(file.classifiers) == 11
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert len(file.requirements) == 1
    assert "numpy" in file.requirements


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

    assert file.has_version is True
    assert file.version == "0.0.1"

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""

    assert file.classifiers
    assert len(file.classifiers) == 11
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert len(file.requirements) == 2
    assert "numpy" in file.requirements
    assert "cython" in file.requirements
    assert file.requirements != []
    for x in file.requirements:
        assert "#" not in x


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

    assert file.has_version is False
    assert file.version is None

    assert file.find_npe2() is None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content == ""

    assert file.classifiers == []
    assert file.requirements == []


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

    assert file.classifiers
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert file.requirements != []
    for x in file.requirements:
        assert "#" not in x


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

    assert file.has_version is True
    assert file.version == "0.0.1"

    assert file.find_npe2() is not None

    d = file.long_description()
    assert d is file.long_description()
    assert file.long_description().raw_content != ""

    assert file.classifiers
    assert len(file.classifiers) == 11
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert len(file.requirements) == 2
    assert "numpy" in file.requirements
    assert "cython" in file.requirements

    assert file.requirements != []
    for x in file.requirements:
        assert "#" not in x


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

    assert file.classifiers == []
    assert file.requirements == []


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

    assert file.classifiers
    assert len(file.classifiers) == 11
    assert "Programming Language :: Python :: 3.9" in file.classifiers

    assert file.requirements == []


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

    delete_file_tree(f"{p.absolute()}")
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


def test_complete_cfg2(resources):
    cfg_file = resources / "complete_setup2.cfg"
    cfg = SetupCfg(cfg_file)

    assert cfg.has_name is True
    assert cfg.name == "napari_svetlana"
    assert cfg.has_author is True
    assert cfg.author == "Clement Cazorla"
    assert cfg.has_summary is True
    assert cfg.summary == "A classification plugin for the ROIs of a segmentation mask."
    assert cfg.has_bugtracker is True
    assert (
        cfg.bugtracker
        == "https://bitbucket.org/koopa31/napari_svetlana/issues?status=new&status=open"
    )
    assert cfg.has_sourcecode is True
    assert cfg.sourcecode == "https://bitbucket.org/koopa31/napari_svetlana/src/main/"
    assert cfg.has_usersupport is True
    assert (
        cfg.usersupport
        == "https://bitbucket.org/koopa31/napari_svetlana/issues?status=new&status=open"
    )


def test_first_pypi_no_file(tmp_path):
    plugin = NapariPlugin(tmp_path)

    assert plugin.first_pypi_config() is None


def test_first_pypi(resources):
    plugin = NapariPlugin(resources / "CZI-29-test")

    assert plugin.first_pypi_config() is plugin.setup_cfg


def test_npe2yaml_creation_setup_py(resources):
    toml = SetupPy(resources / "setup.py")
    with pytest.raises(NotImplementedError):
        toml.create_npe2_entry()


def test_npe2yaml_creation_toml(resources):
    toml = PyProjectToml(resources / "pyproject2.toml")
    path = toml.create_npe2_entry()

    assert path == resources / "myproject" / "napari.yaml"
    assert toml.find_npe2() == path


def test_npe2yaml_creation_cfg(resources):
    cfg = SetupCfg(resources / "setup.cfg")
    path = cfg.create_npe2_entry()

    assert path == resources / "src" / "test-plugin-name" / "napari.yaml"
    assert cfg.find_npe2() == path


def test_npe2yaml_creation_save(resources, monkeypatch):
    plugin = NapariPlugin(resources / "CZI-29-small", forced_gen=2)

    assert plugin.gen == 2

    file = plugin.npe2_yaml
    assert file.exists is False
    assert plugin.npe2_file_location() is None

    file.name = "test plugin"
    file.save()
    assert file.exists is True
    assert (
        plugin.npe2_file_location()
        == resources / "CZI-29-small" / "src" / "test-plugin-name" / "napari.yaml"
    )
    file.file.unlink()


def test_npe2yaml_creation_save_gen1(resources, monkeypatch):
    plugin = NapariPlugin(resources / "CZI-29-small")
    assert plugin.gen == 1

    file = plugin.npe2_yaml
    assert file.exists is False
    assert plugin.npe2_file_location() is None

    file.name = "test plugin"
    file.save()
    assert file.exists is False
    assert plugin.npe2_file_location() is None


def test_plugin_generation(resources):
    plugin = NapariPlugin(resources / "CZI-29-small")

    assert plugin.gen == 1

    plugin = NapariPlugin(resources / "CZI-29-test")

    assert plugin.gen == 2

    plugin = NapariPlugin(resources / "CZI-29-small", forced_gen=2)

    assert plugin.gen == 2


def test_readme_intro_detection(resources):
    readme = MarkdownDescription.from_file(resources / "README2.md")

    assert readme.has_intro is True


def test_markdown_image_detection(resources):
    readme = MarkdownDescription.from_file(resources / "README2.md")

    assert readme.has_videos_or_screenshots is True


def test_markdown_title_extraction(resources):
    readme = MarkdownDescription.from_file(resources / "README2.md")

    title = readme.title

    assert title == "napari-cookiecut: a plugin for napari"


def test_markdown_title_extraction_notitle(resources):
    readme = MarkdownDescription.from_file(resources / "citations" / "citations1.md")

    title = readme.title

    assert title is None


def test_python_version(resources):
    plugin = NapariPlugin(resources / "CZI-29-test")

    assert plugin.supported_python_version
    assert len(plugin.supported_python_version) == 3
    assert (3, 7) in plugin.supported_python_version
    assert (3, 8) in plugin.supported_python_version
    assert (3, 9) in plugin.supported_python_version
    assert (3,) not in plugin.supported_python_version

    plugin = NapariPlugin(resources / "CZI-29-test2")
    assert plugin.supported_python_version
    assert len(plugin.supported_python_version) == 1
    assert plugin.supported_python_version[0] is None

    plugin = NapariPlugin(resources / "CZI-29-small")
    assert plugin.supported_python_version
    assert len(plugin.supported_python_version) == 3
    assert (3, 7) in plugin.supported_python_version
    assert (3, 8) in plugin.supported_python_version
    assert (3, 9) in plugin.supported_python_version
    assert (3,) not in plugin.supported_python_version

    plugin = NapariPlugin(resources / "CZI-29-faulty")
    assert plugin.supported_python_version
    assert len(plugin.supported_python_version) == 1
    assert plugin.supported_python_version[0] is None


def test_platforms(resources):
    plugin = NapariPlugin(resources / "CZI-29-test")

    assert plugin.supported_platforms
    assert len(plugin.supported_platforms) == 3
    assert "win" in plugin.supported_platforms
    assert "linux" in plugin.supported_platforms
    assert "macos" in plugin.supported_platforms

    plugin = NapariPlugin(resources / "CZI-29-test2")
    assert plugin.supported_platforms
    assert len(plugin.supported_platforms) == 2
    assert "win" in plugin.supported_platforms
    assert "linux" in plugin.supported_platforms
    assert "macos" not in plugin.supported_platforms

    plugin = NapariPlugin(resources / "CZI-29-small")
    assert plugin.supported_platforms
    assert len(plugin.supported_platforms) == 1
    assert "macos" in plugin.supported_platforms

    plugin = NapariPlugin(resources / "CZI-29-faulty")
    assert plugin.supported_platforms == [None]


def test_requirements(resources):
    plugin = NapariPlugin(resources / "CZI-29-test")

    requirements = plugin.requirements
    assert requirements.options_list

    assert len(requirements.options_list) == 9
    assert requirements.options_list[0].python_version == (3, 7)
    assert requirements.options_list[0].platforms == WIN64
    assert requirements.options_list[1].python_version == (3, 7)
    assert requirements.options_list[1].platforms == LINUX
    assert requirements.options_list[2].python_version == (3, 7)
    assert requirements.options_list[2].platforms == MACOS

    assert requirements.options_list[3].python_version == (3, 8)
    assert requirements.options_list[3].platforms == WIN64
    assert requirements.options_list[4].python_version == (3, 8)
    assert requirements.options_list[4].platforms == LINUX
    assert requirements.options_list[5].python_version == (3, 8)
    assert requirements.options_list[5].platforms == MACOS

    assert requirements.options_list[6].python_version == (3, 9)
    assert requirements.options_list[6].platforms == WIN64
    assert requirements.options_list[7].python_version == (3, 9)
    assert requirements.options_list[7].platforms == LINUX
    assert requirements.options_list[8].python_version == (3, 9)
    assert requirements.options_list[8].platforms == MACOS

    assert requirements.requirements
    assert len(requirements.requirements) == 3
    assert "JPype1>=1.2.1" in requirements.requirements
    assert "matplotlib" in requirements.requirements
    assert "imageio_ffmpeg" in requirements.requirements


def test_requirements_list(resources):
    plugin = NapariPlugin(resources / "CZI-29-test2")

    reqs = plugin.requirements

    assert reqs.requirements
    assert len(reqs.requirements) == 3
    assert "numpy" in reqs.requirements
    assert "cython" in reqs.requirements
    assert "pyecore==0.13.1" in reqs.requirements


def test_hatch_backend_support_src(resources):
    plugin = NapariPlugin(resources / "CZI-29-test3" / "subproj1-hatch-src")

    pyproject_toml = plugin.pyproject_toml


    npe2location = pyproject_toml.find_npe2()

    assert npe2location
    assert 'src' in str(npe2location)

    npe2file = plugin.npe2_yaml

    assert npe2file
    assert npe2file.name == 'my-napari-plugin'


def test_hatch_backend_support_nosrc(resources):
    plugin = NapariPlugin(resources / "CZI-29-test3" / "subproj2-hatch-nosrc")

    pyproject_toml = plugin.pyproject_toml


    npe2location = pyproject_toml.find_npe2()

    assert npe2location
    assert '/src/napari_plugin' not in str(npe2location)

    npe2file = plugin.npe2_yaml

    assert npe2file
    assert npe2file.name == 'my-napari-plugin'
