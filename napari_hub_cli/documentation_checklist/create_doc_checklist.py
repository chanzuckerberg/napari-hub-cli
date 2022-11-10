from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .filesaccess import NapariPlugin

CHECKLIST_STYLE = {
    True: ("\N{CHECK MARK}", "bold green"),
    False: ("\N{BALLOT X}", "bold red"),
}


@dataclass
class MetaFeature(object):
    name: str
    attribute: str
    advise_location: str


@dataclass
class Feature(object):
    meta: MetaFeature
    found: bool
    found_in: Optional[Path]
    only_in_fallback: bool
    has_fallback_files: bool
    scanned_files: List[Path]


@unique
class AnalysisStatus(Enum):
    SUCCESS = "Success"
    MISSING_URL = "Missing repository URL"
    NON_EXISTING_PLUGIN = "Plugin is not existing in the Napari-HUB plateform"
    UNACCESSIBLE_REPOSITORY = "Repository URL is not accessible"
    BAD_URL = "Repository URL does not have right format"


@dataclass
class PluginAnalysisResult(object):
    features: List[Feature]
    status: AnalysisStatus
    repository: Optional[Path]
    url: Optional[str]

    @classmethod
    def with_status(cls, status, url=None):
        return cls([], status, None, url)


DISPLAY_NAME = MetaFeature("Display Name", "has_name", "npe2 file: napari.yaml")
SUMMARY = MetaFeature("Summary Sentence", "has_summary", ".napari-hub/config.yml")
SOURCECODE = MetaFeature("Source Code", "has_sourcecode", ".napari-hub/config.yml")
AUTHOR = MetaFeature("Author Name", "has_author", ".napari-hub/config.yml")
BUGTRACKER = MetaFeature(
    "Issue Submission Link", "has_bugtracker", ".napari-hub/config.yml"
)
USER_SUPPORT = MetaFeature(
    "Support Channel Link", "has_usersupport", ".napari-hub/config.yml"
)
VIDEO_SCREENSHOT = MetaFeature(
    "Intro Screenshot/Video", "has_videos_or_screenshots", ".napari-hub/DESCRIPTION.yml"
)
USAGE = MetaFeature("Usage Overview", "has_usage", ".napari-hub/DESCRIPTION.md")
INTRO = MetaFeature("Intro Paragraph", "has_intro", ".napari-hub/DESCRIPTION.md")
CITATION = MetaFeature("Citation", "exists", "CITATION.CFF")
CITATION_VALID = MetaFeature("Citation Format is Valid", "is_valid", "CITATION.CFF")


def check_feature(meta, main_file, fallbacks):
    scanned_files = [main_file, *fallbacks]
    has_fallback = len(fallbacks) > 0
    key = f"{meta.attribute}"
    if getattr(main_file, key, False):
        return Feature(meta, True, main_file.file, False, has_fallback, scanned_files)
    for fallback in fallbacks:
        if getattr(fallback, key, False):
            return Feature(meta, True, fallback.file, True, True, scanned_files)
    return Feature(meta, False, None, False, has_fallback, scanned_files)


def create_checklist(repopath):
    """Create the documentation checklist and the subsequent suggestions by looking at metadata in multiple files
    Parameters
    ----------
    repo : str
        local path to the plugin

    Returns
    -------
        Console Checklist and Suggestions

    """
    repo = Path(repopath)
    plugin_repo = NapariPlugin(repo)

    setup_py = plugin_repo.setup_py
    setup_cfg = plugin_repo.setup_cfg
    napari_cfg = plugin_repo.config_yml
    description = plugin_repo.description
    # pyproject_toml = plugin_repo.pyproject_toml  # not used?
    npe2_yaml = plugin_repo.npe2_yaml

    long_descr_setup_cfg = setup_cfg.long_description()
    long_descr_setup_py = setup_py.long_description()

    result = []
    result.append(
        check_feature(
            DISPLAY_NAME, main_file=npe2_yaml, fallbacks=(setup_cfg, setup_py)
        )
    )
    for meta_feature in (SUMMARY, SOURCECODE, AUTHOR, BUGTRACKER, USER_SUPPORT):
        result.append(
            check_feature(
                meta_feature, main_file=napari_cfg, fallbacks=(setup_cfg, setup_py)
            )
        )
    for meta_feature in (VIDEO_SCREENSHOT, USAGE, INTRO):
        result.append(
            check_feature(
                meta_feature,
                main_file=description,
                fallbacks=(long_descr_setup_cfg, long_descr_setup_py),
            )
        )
    for meta_feature in (CITATION, CITATION_VALID):
        result.append(
            check_feature(
                meta_feature, main_file=plugin_repo.citation_file, fallbacks=()
            )
        )
    return PluginAnalysisResult(result, AnalysisStatus.SUCCESS, repo, None)


def display_checklist(analysis_result):
    # get repository for display
    repo = analysis_result.repository.parent

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
            f" ({feature.found_in.relative_to(repo)})" if feature.found else ""
        )
        console.print(f"{mark} {feature.meta.name}{found_localisation}", style=style)

    # Display detailed information
    for feature in analysis_result.features:
        if not feature.only_in_fallback:
            continue
        console.print()
        console.print(
            f"- {feature.meta.name.capitalize()} found only in the fallback file (found in '{feature.found_in.relative_to(repo)}')",
            style="yellow",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")

    # Display detailed information
    for feature in analysis_result.features:
        if feature.found:
            continue
        files = [
            f"{f.file.relative_to(repo)}" for f in feature.scanned_files if f.exists
        ]
        scanned_files = f" (scanned files: {', '.join(files)})" if files else ""
        console.print()
        console.print(
            f"- {feature.meta.name.capitalize()} not found{scanned_files}",
            style="red",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")
