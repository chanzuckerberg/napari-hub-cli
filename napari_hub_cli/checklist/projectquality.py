from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement, RequirementSuite

TITLE = "Code Quality"

# Additional data
HAS_VERSION = MetaFeature("Has explicit version in configuration files", "has_version")
PLUGIN_VERSION = MetaFeature("Plugin version", "version")
TOOL_VERSION = MetaFeature("CLI Tool Version", "get_cli_tool_version")
TIMESTAMP = MetaFeature("Execution Timestamp", "timestamp")
SUPPORTED_PYTHON_VERSIONS = MetaFeature(
    "Supported Python versions", "supported_python_version"
)
SUPPORTED_PLATFORMS = MetaFeature("Supported Platforms", "supported_platforms")
NUMBER_DEPENDENCIES = MetaFeature(
    "Number of Installed Depenencies", "number_of_dependencies"
)
CODECOV_RESULT = MetaFeature("Codecov results", "reported_codecov_result")
NUM_ANALYZED_PYFILES = MetaFeature("Number of analyzed Python files", "number_py_files")

# Checks
HAS_SUPPORT_WIN = MetaFeature("Has explicit Windows support", "has_windows_support")
HAS_SUPPORT_LINX = MetaFeature("Has explicit Linux support", "has_linux_support")
HAS_SUPPORT_MACOS = MetaFeature("Has explicit MacOS support", "has_macos_support")
INSTALLABLE_WIN = MetaFeature("Installable on Windows", "installable_windows")
INSTALLABLE_LINUX = MetaFeature("Installable on Linux", "installable_linux")
INSTALLABLE_MACOS = MetaFeature("Installable on MacOS", "installable_macos")
ALL_WHEELS_WIN = MetaFeature("All deps are wheels for Windows", "allwheel_windows")
ALL_WHEELS_LINUX = MetaFeature("All deps are wheels for Linux", "allwheel_linux")
ALL_WHEELS_MACOS = MetaFeature("All deps are wheels for MacOS", "allwheel_macos")
HAS_C_EXT_WIN = MetaFeature(
    "Has no deps with C extensions for Windows", "has_no_C_ext_windows"
)
HAS_C_EXT_LINUX = MetaFeature(
    "Has no deps with C extensions for Linux", "has_no_C_ext_linux"
)
HAS_C_EXT_MACOS = MetaFeature(
    "Has no deps with C extensions for MacOS", "has_no_C_ext_macos"
)
HAS_GITHUB_WORKFLOWS = MetaFeature("Github Action Workflows are configured", "exists")
HAS_TESTS_WORKFLOWS = MetaFeature(
    "Github Action tests are configured", "gh_test_config"
)
HAS_CODECOV_WORKFLOWS = MetaFeature(
    "Github Action codecov is configured", "gh_codecov_config"
)
HAS_SUCCESS_TESTS = MetaFeature(
    "Tests are passing for main/master branch", "has_successful_tests"
)
HAS_CODE_COV_80 = MetaFeature(
    "Tests cover more than 80% of the code for main/master branch",
    "has_codecove_more_80",
)
HAS_CODE_COV_RESULTS = MetaFeature(
    "Project has codecov result on main/master branch",
    "has_codecove_results",
)
HAS_OSI_LICENSE = MetaFeature("Is licence OSI approved", "is_osi_approved")
NPE2_ERRORS = MetaFeature("Has no npe2 parsing errors", "has_no_npe_parse_errors")
CONDA_LINUX = MetaFeature("Linux bundle support", "is_linux_supported")
CONDA_WIN = MetaFeature("Windows bundle support", "is_windows_supported")
CONDA_MACOS = MetaFeature("MacOS bundle support", "is_macos_supported")
HAD_UNKNOWN_ERROR = MetaFeature(
    "Had no unexpected error during dependency analysis", "had_no_unknown_error"
)
HAS_LICENSE = MetaFeature("Has LICENSE file", "exists")
HAS_NO_PYQT_PYSIDE_DEP = MetaFeature("Has no dependencies to PySide2 or PyQt5", "has_no_forbidden_deps")
HAS_NO_PYQT_PYSIDE_CODE = MetaFeature("Has no code reference to PySide2 or PyQt5", "has_no_forbidden_imports")


def suite_generator(plugin_repo: NapariPlugin):
    requirements = plugin_repo.requirements
    condainfo = plugin_repo.condainfo
    license = plugin_repo.license
    pyproject_toml = plugin_repo.pyproject_toml
    setup_cfg = plugin_repo.setup_cfg
    setup_py = plugin_repo.setup_py
    additional_info = plugin_repo.additional_info
    gh_workflow_folder = plugin_repo.gh_workflow_folder
    linter = plugin_repo.linter
    if gh_workflow_folder.url is None:
        # if there is no url, we cannot query github
        main_gh_workfolder = []
    else:
        main_gh_workfolder = [gh_workflow_folder]  # pragma: no cover
    return RequirementSuite(
        title=TITLE,
        additionals=[
            Requirement(
                features=[HAS_VERSION, PLUGIN_VERSION],
                main_files=[pyproject_toml, setup_cfg, setup_py],
                fallbacks=[],
            ),
            Requirement(
                features=[TOOL_VERSION, TIMESTAMP],
                main_files=[additional_info],
                fallbacks=[],
            ),
            Requirement(
                features=[SUPPORTED_PLATFORMS, SUPPORTED_PYTHON_VERSIONS],
                main_files=[plugin_repo],
                fallbacks=[],
            ),
            Requirement(
                features=[NUMBER_DEPENDENCIES],
                main_files=[requirements],
                fallbacks=[],
            ),
            Requirement(
                features=[CODECOV_RESULT],
                main_files=main_gh_workfolder,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[NUM_ANALYZED_PYFILES],
                main_files=[linter],
                fallbacks=[],
            )
        ],
        requirements=[
            Requirement(
                features=[HAS_LICENSE, HAS_OSI_LICENSE],
                main_files=[license],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    HAS_SUPPORT_LINX,
                    HAS_SUPPORT_MACOS,
                    HAS_SUPPORT_WIN,
                    INSTALLABLE_LINUX,
                    INSTALLABLE_MACOS,
                    INSTALLABLE_WIN,
                    ALL_WHEELS_LINUX,
                    ALL_WHEELS_MACOS,
                    ALL_WHEELS_WIN,
                    HAS_C_EXT_LINUX,
                    HAS_C_EXT_MACOS,
                    HAS_C_EXT_WIN,
                    HAD_UNKNOWN_ERROR,
                ],
                main_files=[requirements],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    NPE2_ERRORS,
                    CONDA_LINUX,
                    CONDA_WIN,
                    CONDA_MACOS,
                ],
                main_files=[condainfo],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    HAS_GITHUB_WORKFLOWS,
                    HAS_TESTS_WORKFLOWS,
                    HAS_CODECOV_WORKFLOWS,
                    HAS_SUCCESS_TESTS,
                    HAS_CODE_COV_RESULTS,
                    HAS_CODE_COV_80,
                ],
                main_files=main_gh_workfolder,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[
                    HAS_NO_PYQT_PYSIDE_DEP,
                ],
                main_files=[requirements],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    HAS_NO_PYQT_PYSIDE_CODE,
                ],
                main_files=[linter],
                fallbacks=[],
            ),
        ],
    )


project_quality_suite = (TITLE, suite_generator)
