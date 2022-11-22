import re
from functools import lru_cache

import yaml

from napari_hub_cli.fs import ConfigFile, Metadata
from napari_hub_cli.fs.descriptions import MarkdownDescription


class SetupPy(Metadata, ConfigFile):
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
        return self.data.get("Bug Tracker")

    @property
    def usersupport(self):
        return self.data.get("projects_urls", {}).get("User Support")

    @usersupport.setter
    def usersupport(self, value):
        self.data.setdefault("project_urls", {})["User Support"] = value

    @property
    def sourcecode(self):
        return self.data.get("projects_urls", {}).get("User Support")

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


class NapariConfig(Metadata, ConfigFile):
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


class SetupCfg(Metadata, ConfigFile):
    @property
    def metadata(self):
        return self.data.get("metadata", {})

    @property
    def project_urls(self):
        return self.metadata.get("project_urls", "")

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
        entries = self.project_urls.split("\n\r")
        for entry in entries:
            k, value = entry.split("=")
            if key in k:
                return value.strip()
        return None

    def _append_value(self, key, value):
        urls = self.data.setdefault("metadata", {}).get("project_urls")
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
    def project_data(self):
        return self.data.get("project", {})

    @property
    def project_urls(self):
        return self.project_data.get("urls", {})

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
        return self.project_urls.get("authors", self.project_urls.get("author"))

    @author.setter
    def author(self, value):
        self.data.setdefault("project", {}).setdefault("urls", {}).setdefault(
            "authors", []
        ).append(value)

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


class Npe2Yaml(Metadata, ConfigFile):
    @property
    def name(self):
        return self.data.get("display_name", self.data.get("name"))

    @name.setter
    def name(self, value):
        self.data["name"] = value


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

    def save(self):
        with self.file.open(mode="w") as f:
            yaml.dump(self.data, stream=f, sort_keys=False)
