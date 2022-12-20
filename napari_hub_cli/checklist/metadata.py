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


ENTRIES_DOC_URL = "https://github.com/chanzuckerberg/napari-hub/wiki/Customizing-your-plugin's-listing"
LABELS_DOC_URL = "https://github.com/chanzuckerberg/napari-hub/wiki/A-plugin-developer%E2%80%99s-guide-to-categories-on-the-napari-hub"


@dataclass
class MetaFeature(object):
    name: str
    attribute: str
    advise_location: str
    automatically_fixable: bool
    doc_url: str
    force_main_file_usage: bool = True


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


DISPLAY_NAME = MetaFeature(
    "Display Name", "has_name", "npe2 file: napari.yaml", True, ENTRIES_DOC_URL
)
SUMMARY = MetaFeature(
    "Summary Sentence", "has_summary", ".napari-hub/config.yml", True, ENTRIES_DOC_URL
)
SOURCECODE = MetaFeature(
    "Source Code", "has_sourcecode", ".napari-hub/config.yml", True, ENTRIES_DOC_URL
)
AUTHOR = MetaFeature(
    "Author Name", "has_author", ".napari-hub/config.yml", True, ENTRIES_DOC_URL
)
BUGTRACKER = MetaFeature(
    "Issue Submission Link",
    "has_bugtracker",
    ".napari-hub/config.yml",
    True,
    ENTRIES_DOC_URL,
)
USER_SUPPORT = MetaFeature(
    "Support Channel Link",
    "has_usersupport",
    ".napari-hub/config.yml",
    True,
    ENTRIES_DOC_URL,
)
VIDEO_SCREENSHOT = MetaFeature(
    "Screenshot/Video",
    "has_videos_or_screenshots",
    ".napari-hub/DESCRIPTION.yml",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
USAGE = MetaFeature(
    "Usage Overview",
    "has_usage",
    ".napari-hub/DESCRIPTION.md",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
INTRO = MetaFeature(
    "Intro Paragraph",
    "has_intro",
    ".napari-hub/DESCRIPTION.md",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
INSTALLATION = MetaFeature(
    "Installation",
    "has_installation",
    ".napari-hub/DESCRIPTION.md",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
CITATION = MetaFeature("Citation", "exists", "CITATION.CFF", True, ENTRIES_DOC_URL)
CITATION_VALID = MetaFeature(
    "Citation Format is Valid", "is_valid", "CITATION.CFF", False, ENTRIES_DOC_URL
)

LABELS = MetaFeature(
    "Labels", "has_labels", ".napari-hub/config.yml", False, LABELS_DOC_URL
)


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


def analyse_local_plugin(repopath):
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

    pyproject_toml, setup_cfg, setup_py = plugin_repo.pypi_files
    napari_cfg = plugin_repo.config_yml
    description = plugin_repo.description
    npe2_yaml = plugin_repo.npe2_yaml

    long_descr_setup_cfg = setup_cfg.long_description()
    long_descr_setup_py = setup_py.long_description()
    long_descr_pyproject_toml = pyproject_toml.long_description()

    requirements = [
        Requirement(
            features=[DISPLAY_NAME],
            main_files=[npe2_yaml],
            fallbacks=[pyproject_toml, setup_cfg, setup_py],
        ),
        Requirement(
            features=[SUMMARY],
            main_files=[napari_cfg],
            fallbacks=[pyproject_toml, setup_cfg, setup_py],
        ),
        Requirement(
            features=[SOURCECODE, AUTHOR, BUGTRACKER, USER_SUPPORT],
            main_files=[pyproject_toml, setup_cfg, setup_py],
            fallbacks=[],
        ),
        Requirement(
            features=[VIDEO_SCREENSHOT, USAGE, INTRO, INSTALLATION],
            main_files=[
                description,
            ],
            fallbacks=[
                long_descr_setup_cfg,
                long_descr_setup_py,
                long_descr_pyproject_toml,
            ],
        ),
        Requirement(
            features=[CITATION, CITATION_VALID],
            main_files=[plugin_repo.citation_file],
            fallbacks=[],
        ),
        Requirement(
            features=[LABELS],
            main_files=[napari_cfg],
            fallbacks=[],
        ),
    ]

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
        if feature.meta is CITATION:
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
