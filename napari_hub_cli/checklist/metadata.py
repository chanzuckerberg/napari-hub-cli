from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import Any, List, Optional, Union

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
class BaseFeature(object):
    meta: MetaFeature
    result: Any


@dataclass
class Feature(BaseFeature):
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
    title: str
    additionals: List[BaseFeature]

    @classmethod
    def with_status(cls, status, title, url=None):
        return cls([], status, None, url, title=title, additionals=[])

    def __getitem__(self, meta):
        return next((f for f in self.features if f.meta is meta))

    def missing_features(self):
        return [feature for feature in self.features if not feature.found]

    def only_in_fallbacks(self):
        return [feature for feature in self.features if feature.only_in_fallback]


@dataclass
class Requirement(object):
    features: List[MetaFeature]
    main_files: List[Union[RepositoryFile, NapariPlugin]]
    fallbacks: List[RepositoryFile]


@dataclass
class RequirementSuite(object):
    title: str
    requirements: List[Requirement]
    additionals: List[Requirement]


def gather_base_feature(meta, main_files):
    key = f"{meta.attribute}"
    res = None
    for main_file in main_files:
        res = getattr(main_file, key)
        if res:
            return BaseFeature(meta, res)
    return BaseFeature(meta, res)


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
        result = getattr(main_file, key)
        if getattr(main_file, key):
            return Feature(
                meta,
                result,
                True,
                main_file,
                False,
                has_fallback,
                scanned_files,
                main_files,
                fallbacks,
            )
    for fallback in fallbacks:
        result = getattr(fallback, key)
        if getattr(fallback, key):
            return Feature(
                meta,
                result,
                True,
                fallback,
                True,
                True,
                scanned_files,
                main_files,
                fallbacks,
            )
    return Feature(
        meta,
        None,
        False,
        None,
        False,
        has_fallback,
        scanned_files,
        main_files,
        fallbacks,
    )


def analyse_requirements(plugin_repo: NapariPlugin, suite: RequirementSuite):
    reqs_result = []
    requirements = suite.requirements
    for requirement in requirements:
        for feature in requirement.features:
            reqs_result.append(
                check_feature(
                    feature,
                    main_files=requirement.main_files,
                    fallbacks=requirement.fallbacks,
                )
            )
    additional_results = []
    for additional in suite.additionals:
        for feature in additional.features:
            additional_results.append(
                gather_base_feature(
                    feature,
                    main_files=additional.main_files,
                )
            )
    return PluginAnalysisResult(
        reqs_result,
        AnalysisStatus.SUCCESS,
        plugin_repo,
        url=None,
        title=suite.title,
        additionals=additional_results,
    )


def analyse_local_plugin(repo_path, requirement_suite):
    """Create the documentation checklist and the subsequent suggestions by looking at metadata in multiple files
    Parameters
    ----------
    repo_path : str
        local path to the plugin
    requirements_suite: Func[NapariPlugin] -> Requirement
        function that takes a NapariPlugin as input and generates the suite to test the repo against

    Returns
    -------
    PluginAnalysisResult:
        the result of the analysis ran against the local repository
    """
    repo = Path(repo_path)
    plugin_repo = NapariPlugin(repo)
    if isinstance(requirement_suite, tuple):
        _, requirement_suite = requirement_suite

    requirements = requirement_suite(plugin_repo)

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
        f"Napari Plugin - {analysis_result.title} Checklist",
        style="bold underline2 blue",
    )

    # Display additional informations
    for feature in analysis_result.additionals:
        console.print(f"  {feature.meta.name}: {feature.result}")

    # Display summary result
    for feature in analysis_result.features:
        if feature.meta.optional:
            console.print()
            console.print("OPTIONAL ", style="underline")
        mark, style = CHECKLIST_STYLE[feature.found]
        found_localisation = (
            f" ({feature.found_in.file.relative_to(repo)})" if feature.found and not feature.found_in.isVirtual else ""
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
        if not feature.meta.advise_location:
            continue
        files = [f"{f.file.relative_to(repo)}" for f in feature.scanned_files]
        scanned_files = f" (scanned files: {', '.join(files)})" if files else ""
        console.print()
        console.print(
            f"- {feature.meta.name.capitalize()} not found or follows an unexpected format{scanned_files}",
            style="red",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")
