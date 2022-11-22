from configparser import ConfigParser
from functools import lru_cache

import tomli
import yaml

from ..utils import parse_setup

format_parsers = {}


def register_parser(extensions):
    def inner(func):
        for extension in extensions:
            format_parsers[extension] = func
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
    with yml_file.open() as fp:
        content = yaml.safe_load(fp)
    if content is not None:
        return content
    return {}


class ConfigFile(object):
    def __init__(self, file):
        self.file = file
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

    @property
    def exists(self):
        return self.file is not None and self.file.exists()


class Exists(object):
    def __init__(self, key):
        self.key = key

    def __get__(self, instance, cls=None):
        return getattr(instance, self.key) is not None


class Metadata(object):  # pragma: no cover
    has_name = Exists("name")
    has_sourcecode = Exists("sourcecode")
    has_usersupport = Exists("usersupport")
    has_bugtracker = Exists("bugtracker")
    has_author = Exists("author")
    has_summary = Exists("summary")


class NapariPlugin(object):
    def __init__(self, path):
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
        if (path / ".napari-hub").exists():
            napari_dir = path / ".napari-hub"
        else:
            napari_dir = path / ".napari"
        self.config_yml = NapariConfig(napari_dir / "config.yml")
        self.description = MarkdownDescription.from_file(napari_dir / "DESCRIPTION.md")
        self.pyproject_toml = PyProjectToml(path / "pyproject.toml")
        self.citation_file = CitationFile(path / "CITATION.cff")
        self.readme = MarkdownDescription.from_file(path / "README.md")

    @property
    @lru_cache(maxsize=1)
    def npe2_yaml(self):
        from .configfiles import Npe2Yaml

        location = self.npe2_file_location()
        return Npe2Yaml(location)

    def npe2_file_location(self):
        for location in (self.setup_py, self.setup_cfg, self.pyproject_toml):
            f = location.find_npe2()
            if f:
                return f
        return None

    @property
    def has_citation_file(self):
        return self.citation_file.exists
