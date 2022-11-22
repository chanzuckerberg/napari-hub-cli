from configparser import ConfigParser
from functools import lru_cache

import tomli
import tomli_w
import yaml

from ..utils import parse_setup

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
    with yml_file.open() as fp:
        content = yaml.safe_load(fp)
    if content is not None:
        return content
    return {}


@register_unparser([".yml", ".YML", ".yaml", ".YAML", ".cff", ".CFF"])
def unparse_yaml(yml_file, data):
    with yml_file.open(mode="w") as f:
        yaml.dump(data, stream=f, sort_keys=False)
    return True


@register_unparser([".cfg", ".CFG"])
def unparse_cfg(cfg_file, data):
    config = ConfigParser()
    config.read_dict(data)
    with cfg_file.open(mode="w") as f:
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

    def save(self):
        return format_unparsers[self.file.suffix](self.file, self.data)


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
