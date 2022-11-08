from dataclasses import dataclass
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
    scanned_files: List[Path]


@dataclass
class PluginAnalysisResult(object):
    features: List[Feature]


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


def check_feature(meta, main_file, fallbacks):
    scanned_files = [main_file, *fallbacks]
    key = f"{meta.attribute}"
    if getattr(main_file, key, False):
        return Feature(meta, True, main_file.file, False, scanned_files)
    for fallback in fallbacks:
        if getattr(fallback, key, False):
            return Feature(meta, True, fallback.file, True, scanned_files)
    return Feature(meta, False, None, False, scanned_files)


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
    result.append(
        check_feature(CITATION, main_file=plugin_repo.citation_file, fallbacks=())
    )
    return PluginAnalysisResult(result)


def display_checklist(analysis_result):

    # setting styles for the checklist
    checked_element, checked_style = CHECKLIST_STYLE[True]
    non_checked_element, unchecked_style = CHECKLIST_STYLE[False]

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
        console.print(f"{mark} {feature.meta.name}", style=style)

    # Display detailed information
    for feature in analysis_result.features:
        if not feature.only_in_fallback:
            continue
        console.print()
        console.print(
            f"- {feature.meta.name} found only in the fallback file (found in '{feature.found_in}')",
            style="yellow",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")

    # Display detailed information
    for feature in analysis_result.features:
        if feature.found:
            continue
        files = [f"{f.file}" for f in feature.scanned_files]
        console.print()
        console.print(
            f"- {feature.meta.name} not found (scanned files: {', '.join(files)})",
            style="red",
        )
        console.print(f"  Recommended file location - {feature.meta.advise_location}")
