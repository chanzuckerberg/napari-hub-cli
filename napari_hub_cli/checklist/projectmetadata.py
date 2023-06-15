from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement, RequirementSuite

ENTRIES_DOC_URL = "https://github.com/chanzuckerberg/napari-hub/wiki/Customizing-your-plugin's-listing"
LABELS_DOC_URL = "https://github.com/chanzuckerberg/napari-hub/wiki/A-plugin-developer%E2%80%99s-guide-to-categories-on-the-napari-hub"

TITLE = "Documentation"

# Additional data
HAS_VERSION = MetaFeature("Has explicit version in configuration files", "has_version")
PLUGIN_VERSION = MetaFeature("Plugin version", "version")
ENGINE_VERSION = MetaFeature("Plugin engine version", "version")

# Checklist
DISPLAY_NAME = MetaFeature(
    "Display Name", "has_name", "npe2 file: napari.yaml", True, ENTRIES_DOC_URL
)
SUMMARY = MetaFeature("Summary Sentence", "has_summary", "", True, ENTRIES_DOC_URL)
SOURCECODE = MetaFeature("Source Code", "has_sourcecode", "", True, ENTRIES_DOC_URL)
AUTHOR = MetaFeature("Author Name", "has_author", "", True, ENTRIES_DOC_URL)
BUGTRACKER = MetaFeature(
    "Issue Submission Link",
    "has_bugtracker",
    "",
    True,
    ENTRIES_DOC_URL,
)
USER_SUPPORT = MetaFeature(
    "Support Channel Link",
    "has_usersupport",
    "",
    True,
    ENTRIES_DOC_URL,
)
VIDEO_SCREENSHOT = MetaFeature(
    "Screenshot/Video",
    "has_videos_or_screenshots",
    "",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
USAGE = MetaFeature(
    "Usage Overview",
    "has_usage",
    "",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
INTRO = MetaFeature(
    "Intro Paragraph",
    "has_intro",
    "",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
INSTALLATION = MetaFeature(
    "Installation",
    "has_installation",
    "",
    False,
    ENTRIES_DOC_URL,
    force_main_file_usage=False,
)
CITATION = MetaFeature(
    "Citation", "exists", "CITATION.CFF", True, ENTRIES_DOC_URL, optional=True
)
CITATION_VALID = MetaFeature(
    "Citation Format is Valid", "is_valid", "CITATION.CFF", False, ENTRIES_DOC_URL
)

LABELS = MetaFeature(
    "Labels", "has_labels", ".napari-hub/config.yml", False, LABELS_DOC_URL
)


def suite_generator(plugin_repo: NapariPlugin):
    pyproject_toml, setup_cfg, setup_py = plugin_repo.pypi_files
    napari_cfg = plugin_repo.config_yml
    description = plugin_repo.description
    npe2_yaml = plugin_repo.npe2_yaml

    long_descr_setup_cfg = setup_cfg.long_description()
    long_descr_setup_py = setup_py.long_description()
    long_descr_pyproject_toml = pyproject_toml.long_description()

    return RequirementSuite(
        title=TITLE,
        additionals=[
            Requirement(
                features=[HAS_VERSION, PLUGIN_VERSION],
                main_files=[pyproject_toml, setup_cfg, setup_py],
                fallbacks=[],
            ),
            Requirement(
                features=[ENGINE_VERSION],
                main_files=[npe2_yaml],
                fallbacks=[],
            ),
        ],
        requirements=[
            Requirement(
                features=[DISPLAY_NAME],
                main_files=[npe2_yaml],
                fallbacks=[pyproject_toml, setup_cfg, setup_py],
            ),
            Requirement(
                features=[SUMMARY, AUTHOR],
                main_files=[pyproject_toml, setup_cfg, setup_py],
                fallbacks=[napari_cfg],
            ),
            Requirement(
                features=[SOURCECODE, BUGTRACKER, USER_SUPPORT],
                main_files=[pyproject_toml, setup_cfg, setup_py],
                fallbacks=[],
            ),
            Requirement(
                features=[INTRO, VIDEO_SCREENSHOT, USAGE, INSTALLATION],
                main_files=[
                    long_descr_setup_cfg,
                    long_descr_setup_py,
                    long_descr_pyproject_toml,
                    description,
                ],
                fallbacks=[],
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
        ],
    )


project_metadata_suite = (TITLE, suite_generator)
