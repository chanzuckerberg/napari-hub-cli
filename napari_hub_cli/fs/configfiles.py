import re
from functools import lru_cache

from ..fs import ConfigFile
from .descriptions import MarkdownDescription


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
    has_version = Exists("version")


class SetupPy(Metadata, ConfigFile):
    @property
    def version(self):
        return self.data.get("version")

    @property
    def name(self):
        return self.data.get("display_name", self.data.get("name"))

    @name.setter
    def name(self, value):
        self.data["name"] = value

    @property
    def author(self):
        return self.data.get("author", self.data.get("authors"))

    @author.setter
    def author(self, value):
        self.data["author"] = value

    @property
    def bugtracker(self):
        data = self.data.get("project_urls", {})
        return data.get("Bug Tracker", data.get("Tracker"))

    @bugtracker.setter
    def bugtracker(self, value):
        self.data.setdefault("project_urls", {})["Bug Tracker"] = value

    @property
    def usersupport(self):
        data = self.data.get("project_urls", {})
        return data.get("User Support", data.get("Support"))

    @usersupport.setter
    def usersupport(self, value):
        self.data.setdefault("project_urls", {})["User Support"] = value

    @property
    def sourcecode(self):
        data = self.data.get("project_urls", {})
        return data.get("Source Code", data.get("Source"))

    @sourcecode.setter
    def sourcecode(self, value):
        self.data.setdefault("project_urls", {})["Source"] = value

    @property
    def summary(self):
        return self.data.get("summary", self.data.get("description"))

    @summary.setter
    def summary(self, value):
        self.data["description"] = value

    @lru_cache(maxsize=1)
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

    def create_npe2_entry(self):
        raise NotImplementedError("Modification of setup.py is not yet supported")

    @property
    def classifiers(self):
        return self.data.get("classifiers", [])

    @property
    def requirements(self):
        return [s.split("#")[0].strip() for s in self.data.get("install_requires", [])]


class NapariConfig(Metadata, ConfigFile):
    has_labels = Exists("labels")

    @property
    def summary(self):
        return self.data.get("summary")

    @summary.setter
    def summary(self, value):
        self.data["summary"] = value

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

    @property
    def labels(self):
        return self.data.get("labels")


class SetupCfg(Metadata, ConfigFile):
    @property
    def metadata(self):
        return self.data.get("metadata", {})

    @property
    def project_urls(self):
        return self.metadata.get("project_urls", "")

    @property
    def version(self):
        return self.metadata.get("version")

    @property
    def name(self):
        return self.metadata.get("display_name", self.metadata.get("name"))

    @name.setter
    def name(self, value):
        self.data.setdefault("metadata", {})["name"] = value

    @property
    def author(self):
        return self.metadata.get("author", self.metadata.get("authors"))

    @author.setter
    def author(self, value):
        self.data.setdefault("metadata", {})["author"] = value

    def _search_url(self, key):
        if not self.project_urls:
            return None
        # entries = re.split(r"\n|\r", self.project_urls)
        entries = self.project_urls.splitlines()
        for entry in entries:
            if not entry:
                continue
            k, value = [s for s in re.split(r"^([^=]+)\=", entry) if s]
            if key in k:
                return value.strip()
        return None

    def _append_value(self, key, value):
        urls = self.data.setdefault("metadata", {}).get("project_urls", "")
        self.data["metadata"]["project_urls"] = f"{urls}\n{key} = {value}"

    @property
    def sourcecode(self):
        return self._search_url("Source")

    @sourcecode.setter
    def sourcecode(self, value):
        self._append_value("Source Code", value)

    @property
    def bugtracker(self):
        return self._search_url("Tracker")

    @bugtracker.setter
    def bugtracker(self, value):
        self._append_value("Bug Tracker", value)

    @property
    def usersupport(self):
        return self._search_url("Support")

    @usersupport.setter
    def usersupport(self, value):
        self._append_value("User Support", value)

    @property
    def summary(self):
        return self.metadata.get("summary", self.metadata.get("description"))

    @summary.setter
    def summary(self, value):
        self.data.setdefault("metadata", {})["description"] = value

    @lru_cache(maxsize=1)
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

    def _find_src_location(self):
        try:
            return self.data["options.packages.find"]["where"]
        except KeyError:
            return ""

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
            src_location = self._find_src_location()
            if src_location:
                modules.insert(0, src_location)
            return self.file.parent.joinpath(*modules) / f"{parsed['file']}.yaml"
        return None

    def create_npe2_entry(self):
        project_name = self.metadata["name"]
        manifest_entry = self.data.setdefault("options.entry_points", {})
        manifest_entry[
            "napari.manifest"
        ] = f"{project_name} = {project_name}:napari.yaml"
        modules = [self._find_src_location()]
        return self.file.parent.joinpath(*modules) / project_name / "napari.yaml"

    @property
    def classifiers(self):
        return [s for s in self.metadata.get("classifiers", "").splitlines() if s]

    @property
    def requirements(self):
        return [
            s.split("#")[0].strip()
            for s in self.data.get("options", {})
            .get("install_requires", "")
            .splitlines()
            if s
        ]


class PyProjectToml(Metadata, ConfigFile):
    @property
    def project_data(self):
        return self.data.get("project", {})

    @property
    def project_urls(self):
        return self.project_data.get("urls", {})

    @property
    def version(self):
        return self.project_data.get("version")

    @property
    def name(self):
        return self.project_data.get("display_name", self.project_data.get("name"))

    @name.setter
    def name(self, value):
        self.data.setdefault("project", {})["name"] = value

    @property
    def sourcecode(self):
        return self.project_urls.get("Source Code", self.project_urls.get("Code"))

    @sourcecode.setter
    def sourcecode(self, value):
        self.data.setdefault("project", {}).setdefault("urls", {})[
            "Source Code"
        ] = value

    @property
    def author(self):
        return self.project_data.get("authors", self.project_data.get("author"))

    @author.setter
    def author(self, value):
        self.data.setdefault("project", {}).setdefault("authors", []).append(value)

    @property
    def bugtracker(self):
        return self.project_urls.get("Bug Tracker", self.project_urls.get("Tracker"))

    @bugtracker.setter
    def bugtracker(self, value):
        self.data.setdefault("project", {}).setdefault("urls", {})[
            "Bug Tracker"
        ] = value

    @property
    def usersupport(self):
        return self.project_urls.get("User Support", self.project_urls.get("Support"))

    @usersupport.setter
    def usersupport(self, value):
        self.data.setdefault("project", {}).setdefault("urls", {})[
            "User Support"
        ] = value

    @property
    def summary(self):
        return self.project_data.get("description")

    @summary.setter
    def summary(self, value):
        self.data.setdefault("project", {})["description"] = value

    @lru_cache(maxsize=1)
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

    def create_npe2_entry(self):
        project_name = self.project_data["name"]
        manifest_entry = (
            self.data.setdefault("project", {})
            .setdefault("entry-points", {})
            .setdefault("napari.manifest", {})
        )
        manifest_entry[project_name] = f"{project_name}:napari.yaml"
        modules = self._find_src_location()
        return self.file.parent.joinpath(*modules) / project_name / "napari.yaml"

    @property
    def classifiers(self):
        return self.project_data.get("classifiers", [])

    @property
    def requirements(self):
        return self.project_data.get("dependencies", [])


class Npe2Yaml(Metadata, ConfigFile):
    def __init__(self, file, plugin=None):
        super().__init__(file)
        self.plugin = plugin

    @property
    def name(self):
        return self.data.get("display_name")

    @name.setter
    def name(self, value):
        self.data["display_name"] = value

    def save(self):
        if self.file:
            super().save()
            return
        assert self.plugin
        if self.plugin.gen == 1:
            return
        config = self.plugin.first_pypi_config()
        location = config.create_npe2_entry()
        self.file = location
        super().save()

    @property
    def version(self):
        return "npe2" if self.file and self.file.exists() else "npe1"

    @property
    def is_npe2(self):
        return self.version == "npe2"


class CitationFile(ConfigFile):
    message_no_preferred = "If you use this plugin, please cite it using these metadata"
    message_preferred = "If you use this software, please cite both the article from preferred-citation and the software itself."
    metadata = {
        "cff-version": "1.2.0",
        "message": "If you use this plugin, please cite it using these metadata",
    }

    def add_header(self):
        self.data.update(self.metadata)

    def update_data(self, d):
        self.data.update(d)

    def override_with(self, citation):
        self.update_data(citation.as_dict())

    def append_citations(self, citations):
        if not citations:
            self.data["message"] = self.message_no_preferred
            return
        self.data["message"] = self.message_preferred
        preferred, *references = citations
        self.data["preferred-citation"] = preferred.as_dict()
        if references:
            self.data["references"] = [r.as_dict() for r in references]
