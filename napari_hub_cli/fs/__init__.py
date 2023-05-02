from configparser import ConfigParser
from functools import lru_cache

import tomli
import tomli_w
import yaml

from ..utils import delete_file_tree, parse_setup

format_parsers = {}
format_unparsers = {}


def register_parser(extensions):
    def inner(func):
        for extension in extensions:
            format_parsers[extension] = func
        return func

    return inner


def register_unparser(extensions):
    def inner(func):
        for extension in extensions:
            format_unparsers[extension] = func
        return func

    return inner


@register_parser([".cfg", ".CFG"])
def parse_cfg(cfg_file):
    config = ConfigParser()
    config.read(f"{cfg_file}")
    content = {}
    for section in config.sections():
        content[section] = dict(config[section])
    return content


@register_parser([".toml", ".TOML"])
def parse_toml(toml_file):
    with toml_file.open(mode="rb") as f:
        content = tomli.load(f)
    return content


# @register_parser([".md", ".MD"])
# def parse_md(md):
#     with md.open():
#         content = md.read_text()
#     return Document(content)


@register_parser([".py"])
def parse_py(py_file):
    return parse_setup(f"{py_file.absolute()}")


@register_parser([".yml", ".YML", ".yaml", ".YAML", ".cff", ".CFF"])
def parse_yaml(yml_file):
    with yml_file.open(encoding="utf-8") as fp:
        content = yaml.safe_load(fp)
    if content is not None:
        return content
    return {}


@register_unparser([".yml", ".YML", ".yaml", ".YAML", ".cff", ".CFF"])
def unparse_yaml(yml_file, data):
    with yml_file.open(mode="w", encoding="utf-8") as f:
        yaml.dump(data, stream=f, sort_keys=False, allow_unicode=True)
    return True


@register_unparser([".cfg", ".CFG"])
def unparse_cfg(cfg_file, data):
    config = ConfigParser()
    config.read_dict(data)
    with cfg_file.open(mode="w", encoding="utf-8") as f:
        config.write(f)
    return True


@register_unparser([".py"])
def unparse_py(py_file, data):
    print("Unparsing of .py files is not yet supported")
    return False


@register_unparser([".toml", ".TOML"])
def unparse_toml(toml_file, data):
    with toml_file.open(mode="wb") as f:
        content = tomli_w.dump(data, f)
    return content


class RepositoryFile(object):
    def __init__(self, file):
        self.file = file

    @property
    def exists(self):
        return self.file is not None and self.file.exists()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.file == other.file

    def __hash__(self):
        return object.__hash__(self)


class ConfigFile(RepositoryFile):
    def __init__(self, file):
        super().__init__(file)
        if self.exists:
            try:
                self.data = format_parsers[file.suffix](file)
                self.is_valid = True
            except Exception:
                self.data = {}
                self.is_valid = False
        else:
            self.data = {}
            self.is_valid = False

    def save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        return format_unparsers[self.file.suffix](self.file, self.data)


class NapariPlugin(object):
    def __init__(self, path, forced_gen=0):
        from .configfiles import (
            CitationFile,
            NapariConfig,
            PyProjectToml,
            SetupCfg,
            SetupPy,
        )
        from .descriptions import MarkdownDescription

        self.path = path
        self.setup_py = SetupPy(path / "setup.py")
        self.setup_cfg = SetupCfg(path / "setup.cfg")
        if (path / ".napari").exists():
            napari_dir = path / ".napari"
        else:
            napari_dir = path / ".napari-hub"
        self.config_yml = NapariConfig(napari_dir / "config.yml")
        self.description = MarkdownDescription.from_file(napari_dir / "DESCRIPTION.md")
        self.pyproject_toml = PyProjectToml(path / "pyproject.toml")
        self.citation_file = CitationFile(path / "CITATION.cff")
        self.readme = MarkdownDescription.from_file(path / "README.md")
        self.forced_gen = forced_gen

    @property
    def summary(self):
        return self.extractfrom_config("summary")

    @property
    def classifiers(self):
        return self.extractfrom_config("classifiers", default=())

    @lru_cache()
    def extractfrom_config(self, attribute, default=None):
        for f in self.pypi_files:
            value = getattr(f, attribute)
            if value:
                return value
        return default

    def first_pypi_config(self):
        for f in self.pypi_files:
            if f.has_name:
                return f
        return None

    @property
    def gen(self):
        if self.forced_gen:
            return self.forced_gen
        if self.npe2_yaml.exists:
            return 2
        return 1

    @property
    @lru_cache(maxsize=1)
    def npe2_yaml(self):
        from .configfiles import Npe2Yaml

        location = self.npe2_file_location()
        return Npe2Yaml(location, self)

    def npe2_file_location(self):
        for location in self.pypi_files:
            f = location.find_npe2()
            if f:
                return f
        return None

    @property
    @lru_cache()
    def pypi_files(self):
        """Returns the PyPi files in preference order (from the most to the less prioritary)

        Returns:
            ConfigFile: the PyPi files from the repository
        """
        return self.pyproject_toml, self.setup_cfg, self.setup_py

    @property
    def has_citation_file(self):
        return self.citation_file.exists

    @property
    def exists(self):
        return self.path.exists()

    def delete(self):
        """Deletes the path towards the repository on the File System"""
        delete_file_tree(f"{self.path.absolute()}")

    @property
    def supported_python_version(self):
        classifiers = self.classifiers
        if not classifiers:
            return ((3, ), )
        versions = []
        for entry in classifiers:
            if "Programming Language :: Python ::" not in entry:
                continue
            version = entry.split(" :: ")[2].split(".")
            versions.append(tuple(int(n) for n in version))
        if len(versions) == 1 and len(versions[0]):
            # If only "python 3" without more information, we will consider the current version
            return versions
        return tuple(v for v in versions if len(v) > 1)

    @property
    def supported_platforms(self):
        classifiers = self.classifiers
        if not classifiers:
            return None
        platforms = set()
        for entry in classifiers:
            if "Operating System" not in entry:
                continue
            if "OS Independent" in entry:
                return ("win", "linux", "macos")
            platform = entry.lower()
            if "windows" in platform:
                platforms.add("win")
            if "linux" in platform:
                platforms.add("linux")
            if "macos" in platform:
                platforms.add("macos")
        return platforms