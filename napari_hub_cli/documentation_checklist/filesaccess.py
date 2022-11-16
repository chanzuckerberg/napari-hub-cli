import re
from configparser import ConfigParser
from functools import lru_cache

import tomli
import yaml
from iguala import cond, match, regex
from mistletoe import Document
from mistletoe.block_token import Heading
from mistletoe.span_token import RawText

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


class Metadata(object):  # pragma: no cover
    @property
    def has_name(self):
        raise NotImplementedError()

    @property
    def has_sourcecode(self):
        raise NotImplementedError()

    @property
    def has_usersupport(self):
        raise NotImplementedError()

    @property
    def has_bugtracker(self):
        raise NotImplementedError()

    # @property
    # def has_long_description(self):
    #     raise NotImplementedError()

    # @property
    # def has_description(self):
    #     raise NotImplementedError()

    @property
    def has_author(self):
        raise NotImplementedError()


class SetupPy(Metadata, ConfigFile):
    @property
    def has_name(self):
        return "name" in self.data or "display_name" in self.data

    @property
    def has_author(self):
        return "author" in self.data or "authors" in self.data

    @property
    def has_bugtracker(self):
        return "Bug Tracker" in self.data.get("projects_urls", {})

    @property
    def has_usersupport(self):
        return "User Support" in self.data.get("projects_urls", {})

    @property
    def has_sourcecode(self):
        return "Source Code" in self.data.get("projects_urls", {})

    @property
    def has_summary(self):
        return "summary" in self.data or "description" in self.data

    @lru_cache()
    def long_description(self):
        content = self.data.get("long_description", "")
        return MarkdownDescription(content, self.file)

    def find_npe2(self):
        try:
            manifest_files = self.data["entry_points"]["napari.manifest"]
        except KeyError:
            return None
        pattern = re.compile(r"[^=]+\s*=\s*(?P<modules>[^:]+\:)(?P<file>(.*?))\.yaml")
        for file in manifest_files:
            result = pattern.match(file)
            if result:
                parsed = result.groupdict()
                modules = [m for m in parsed["modules"].split(":") if m]
                return self.file.parent.joinpath(*modules) / f"{parsed['file']}.yaml"
        return None


class NapariConfig(Metadata, ConfigFile):
    @property
    def has_summary(self):
        return "summary" in self.data

    @property
    def has_author(self):
        return "author" in self.data or "authors" in self.data

    @property
    def has_bugtracker(self):
        return "Bug Tracker" in self.data or "Report Issues" in self.data

    @property
    def has_usersupport(self):
        return "User Support" in self.data

    @property
    def has_projectsite(self):
        return "Project Site" in self.data

    @property
    def has_sourcecode(self):
        return "Source Code" in self.data


class SetupCfg(Metadata, ConfigFile):
    @property
    @lru_cache()
    def metadata(self):
        return self.data.get("metadata", {})

    @property
    @lru_cache()
    def project_urls(self):
        return self.metadata.get("project_urls", "")

    @property
    def has_name(self):
        return "name" in self.metadata or "display_name" in self.metadata

    @property
    def has_author(self):
        return "author" in self.metadata or "authors" in self.metadata

    @property
    def has_sourcecode(self):
        return "Source Code" in self.project_urls or "Source" in self.project_urls

    @property
    def has_bugtracker(self):
        return "Bug Tracker" in self.project_urls or "Tracker" in self.project_urls

    @property
    def has_usersupport(self):
        return "User Support" in self.project_urls or "Support" in self.project_urls

    @property
    def has_summary(self):
        return "summary" in self.metadata or "description" in self.metadata

    @lru_cache()
    def long_description(self):
        try:
            descr = f"{self.data['metadata']['long_description']}"
        except KeyError:
            return MarkdownDescription("", self.file)
        if descr.startswith("file: "):
            readme_name = descr.replace("file: ", "").strip()
            readme = self.file.parent / readme_name
            return MarkdownDescription.from_file(readme)
        return MarkdownDescription("", self.file)

    def find_npe2(self):
        try:
            manifest = self.data["options.entry_points"]["napari.manifest"]
        except KeyError:
            return None
        pattern = re.compile(r"[^=]+\s*=\s*(?P<modules>[^:]+\:)(?P<file>(.*?))\.yaml")
        result = pattern.match(manifest)
        if result:
            parsed = result.groupdict()
            modules = [m for m in parsed["modules"].split(":") if m]
            src_location = self.data.get("options.packages.find", {}).get("where", "")
            if src_location:
                modules.insert(0, src_location)
            return self.file.parent.joinpath(*modules) / f"{parsed['file']}.yaml"
        return None


class PyProjectToml(Metadata, ConfigFile):
    @property
    @lru_cache
    def project_data(self):
        return self.data.get("project", {})

    @property
    @lru_cache
    def project_urls(self):
        return self.project_data.get("urls", {})

    @property
    def has_name(self):
        return "name" in self.project_data or "display_name" in self.project_data

    @property
    def has_sourcecode(self):
        return "Source Code" in self.project_urls or "Source" in self.project_urls

    @property
    def has_author(self):
        return "authors" in self.project_data or "author" in self.project_data

    @property
    def has_bugtracker(self):
        return "Bug Tracker" in self.project_urls or "Tracker" in self.project_urls

    @property
    def has_usersupport(self):
        return "User Support" in self.project_urls or "Support" in self.project_urls

    @property
    def has_summary(self):
        return "description" in self.project_data

    @lru_cache()
    def long_description(self):
        try:
            readme_name = self.project_data["readme"]
            readme = self.file.parent / readme_name
            return MarkdownDescription.from_file(readme)
        except KeyError:
            return MarkdownDescription("", self.file)

    def _find_src_location(self):
        try:
            return self.data["tool"]["setuptools"]["packages"]["find"]["where"]
        except KeyError:
            return []

    def find_npe2(self):
        try:
            manifest_entry = self.project_data["entry-points"]["napari.manifest"]
        except KeyError:
            return None
        project_name = self.project_data.get("name", "")
        manifest = manifest_entry[project_name]
        modules = self._find_src_location()
        pattern = re.compile(r"(?P<modules>[^:]+\:)(?P<file>(.*?))\.yaml")
        result = pattern.match(manifest)
        if result:
            parsed = result.groupdict()
            modules.extend(m for m in parsed["modules"].split(":") if m)
            return self.file.parent.joinpath(*modules) / f"{parsed['file']}.yaml"
        return None


class Npe2Yaml(Metadata, ConfigFile):
    @property
    def has_name(self):
        return "name" in self.data or "display_name" in self.data


class MarkdownDescription(object):
    def __init__(self, raw_content, file):
        self.file = file
        self.raw_content = re.sub("(<!--.*?-->)", "", raw_content, flags=re.DOTALL)
        self.content = Document(self.raw_content)

    @classmethod
    def from_file(cls, file):
        try:
            with file.open():
                content = file.read_text()
            return cls(content, file)
        except FileNotFoundError:
            return cls("", file)

    @property
    def exists(self):
        return self.file is not None and self.file.exists()

    @property
    def has_videos(self):
        pattern = match(Document) % {
            "children+>content": regex(r"^http(s)?://.*?\.(mp4|avi|mpeg)$")
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_screenshots(self):
        pattern = match(Document) % {
            "children+>src": regex(r"^(?!http).*?\.(png|jpeg|jpg|svg)$")
        }
        result = pattern.match(self.content)
        if result.is_match:
            return True

        def is_img(__self__):
            e = __self__
            if "<img" not in e:
                return False
            img_pattern = re.compile(r"^(?!http).*?\.(png|jpeg|jpg|svg)$")
            tags = e.split()
            for tag in tags:
                if not tag.startswith("src"):
                    continue
                tag = tag[5:-1]
                return img_pattern.match(tag) is not None

        pattern = match(Document) % {"children+>content": cond(is_img)}
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_videos_or_screenshots(self):
        return self.has_videos or self.has_screenshots

    @property
    def has_usage(self):
        pattern = match(Document) % {
            "children": match(Heading)
            % {
                "level": range(2, 5),  # Must be a heading of at least 2
                "children*>content": regex(
                    r"^.*?[Uu]sage"  # Must contain "usage" in the title
                ),
            }
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_installation(self):
        pattern = match(Document) % {
            "children+>content": regex(
                r"^.*?(pip|conda)\s+install"  # Must contain "pip install"
            ),
        }
        result = pattern.match(self.content)
        return result.is_match

    @property
    def has_intro(self):
        pattern = match(Document) % {
            "children": [
                ...,
                match(Heading) % {"level": 1},
                "*paragraphs",
                match(Heading) % {"level": 2},
                ...,
            ]
        }
        result = pattern.match(self.content)
        if result.is_match:
            paragraphs = result.bindings[0]["paragraphs"]

            def is_txt(p):
                if not hasattr(p, "children"):
                    return False
                for child in p.children:
                    if not isinstance(child, RawText):
                        continue
                    if child.content.startswith("<") or child.content[-1] == ">":
                        continue
                    return True
                return False

            return len(paragraphs) > 0 and any(is_txt(p) for p in paragraphs)
        return False


class CitationFile(ConfigFile):
    ...


class NapariPlugin(object):
    def __init__(self, path):
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

    @property
    @lru_cache()
    def npe2_yaml(self):
        location = self.npe2_file_location()
        return Npe2Yaml(location)

    def npe2_file_location(self):
        for location in (self.setup_py, self.setup_cfg, self.pyproject_toml):
            f = location.find_npe2()
            if f:
                return f
        return None

    @property
    def has_citation(self):
        return self.citation_file.exists
