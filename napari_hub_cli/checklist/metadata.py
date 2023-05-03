from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from ..fs import NapariPlugin, RepositoryFile

CHECKLIST_STYLE = {
    True: ("\N{CHECK MARK}", "bold green"),
    False: ("\N{BALLOT X}", "bold red"),
}


@dataclass
class MetaFeature(object):
    name: str
    attribute: str
    advise_location: str = ""
    automatically_fixable: bool = False
    doc_url: str = ""
    force_main_file_usage: bool = True
    optional: bool = False


@dataclass
class Feature(object):
    meta: MetaFeature
    found: bool
    found_in: Optional[RepositoryFile]
    only_in_fallback: bool
    has_fallback_files: bool
    scanned_files: List[RepositoryFile]
    main_files: List[RepositoryFile]
    fallbacks: List[RepositoryFile]


@unique
class AnalysisStatus(Enum):
    SUCCESS = "Success"
    MISSING_URL = "Missing repository URL"
    NON_EXISTING_PLUGIN = "Plugin is not existing in the Napari-HUB platform"
    UNACCESSIBLE_REPOSITORY = "Repository URL is not accessible"
    BAD_URL = "Repository URL does not have right format"


@dataclass
class PluginAnalysisResult(object):
    features: List[Feature]
    status: AnalysisStatus
    repository: Optional[NapariPlugin]
    url: Optional[str]

    @classmethod
    def with_status(cls, status, url=None):
        return cls([], status, None, url)

    def __getitem__(self, meta):
        return next((f for f in self.features if f.meta is meta))

    def missing_features(self):
        return [feature for feature in self.features if not feature.found]

    def only_in_fallbacks(self):
        return [feature for feature in self.features if feature.only_in_fallback]


@dataclass
class Requirement(object):
    features: List[MetaFeature]
    main_files: List[RepositoryFile]
    fallbacks: List[RepositoryFile]


def check_feature(meta, main_files, fallbacks):
    """Checks for a metadata presence in primary and secondary sources
    Parameters
    ----------
    meta: MetaFeature
        the feature that needs to be checked
    main_files: Iterable[ConfigFile]
        the primary source files list
    fallbacks: Iterable[ConfigFile]
        the secondary source files

    Returns
    -------
    Feature:
        the result of the analysis of the metadata presence
    """
    scanned_files = [*main_files, *fallbacks]
    has_fallback = len(fallbacks) > 0
    key = f"{meta.attribute}"
    for main_file in main_files:
        if getattr(main_file, key):
            return Feature(
                meta,
                True,
                main_file,
                False,
                has_fallback,
                scanned_files,
                main_files,
                fallbacks,
            )
    for fallback in fallbacks:
        if getattr(fallback, key):
            return Feature(
                meta, True, fallback, True, True, scanned_files, main_files, fallbacks
            )
    return Feature(
        meta, False, None, False, has_fallback, scanned_files, main_files, fallbacks
    )


def analyse_requirements(plugin_repo: NapariPlugin, requirements):
    result = []
    for requirement in requirements:
        for feature in requirement.features:
            result.append(
                check_feature(
                    feature,
                    main_files=requirement.main_files,
                    fallbacks=requirement.fallbacks,
                )
            )
    return PluginAnalysisResult(result, AnalysisStatus.SUCCESS, plugin_repo, None)


def analyse_local_plugin_metadata(repopath):
    """Create the documentation checklist and the subsequent suggestions by looking at metadata in multiple files
    Parameters
    ----------
    repo : str
        local path to the plugin

    Returns
    -------
    PluginAnalysisResult:
        the result of the analysis ran against the local repository
    """
    repo = Path(repopath)
    plugin_repo = NapariPlugin(repo)

    from .projectmetadata import project_metadata_check

    requirements = project_metadata_check(plugin_repo)

    return analyse_requirements(plugin_repo, requirements)


def display_checklist(analysis_result):
    """Displays to the screen the result of the analysis of a plugin
    Parameters
    ----------
    analysis_result: PluginAnalysisResult
        the result of the analysis ran against the local repository
    """
    # get repository for display
    repo = analysis_result.repository.path.parent if analysis_result.repository else ""

    # create the Console Documentation Checklist
    console = Console()
    console.print()
    console.print(
        "Napari Plugin - Documentation Checklist", style="bold underline2 blue"
    )

    # Display summary result
    for feature in analysis_result.features:
        if feature.meta.optional:
            console.print()
            console.print("OPTIONAL ", style="underline")
        mark, style = CHECKLIST_STYLE[feature.found]
        found_localisation = (
            f" ({feature.found_in.file.relative_to(repo)})" if feature.found else ""
        )
        console.print(f"{mark} {feature.meta.name}{found_localisation}", style=style)

    # Display detailed information
    for feature in analysis_result.only_in_fallbacks():
        if feature.meta.automatically_fixable:
            continue
        console.print()
        preferred_sources = [
            x for x in feature.scanned_files if x not in feature.fallbacks
        ]
        if not preferred_sources:
            preferred_sources = feature.main_files
        preferred_sources = [f"`{f.file.relative_to(repo)}`" for f in preferred_sources]
        if not feature.meta.force_main_file_usage:
            if feature.main_files[0].exists:
                console.print(
                    f"- {feature.meta.name} was found in `{feature.found_in.file.relative_to(repo)}`. You can also place this information in your {' or '.join(preferred_sources)} if you want.",
                    style="yellow",
                )
            continue
        console.print(
            f"- {feature.meta.name.capitalize()} found only in the fallback file (found in '{feature.found_in.file.relative_to(repo)}')",
            style="yellow",
        )
        console.print(f"  Recommended file location - {preferred_sources}")

    # Display detailed information
    for feature in analysis_result.missing_features():
        files = [f"{f.file.relative_to(repo)}" for f in feature.scanned_files]
        scanned_files = f" (scanned files: {', '.join(files)})" if files else ""
        console.print()
        console.print(
            f"- {feature.meta.name.capitalize()} not found or follows an unexpected format{scanned_files}",
            style="red",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")
