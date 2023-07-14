from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement, RequirementSuite, Section

from rich import print

TITLE = "Code Quality"

#Sections

license_section = Section(title="License")
testing_section = Section(title="Testing")
npe_section = Section(title="Napari Plugin Engine")
os_section = Section(title="OS Support")
install_section = Section(title="Installation")
dependencies_section = Section(title="Forbidden Dependencies")
error_section = Section(title="Errors")
conda_section = Section(title="Conda Installation")
additional_info_section = Section(title="More Details")


# Additional data
HAS_VERSION = MetaFeature("Has explicit version in configuration files", "has_version", section=additional_info_section)
PLUGIN_VERSION = MetaFeature("Plugin version", "version", section=additional_info_section)
ENGINE_VERSION = MetaFeature("Plugin engine version", "version", section=additional_info_section)
TOOL_VERSION = MetaFeature("CLI Tool Version", "get_cli_tool_version", section=additional_info_section)
TIMESTAMP = MetaFeature("Execution Timestamp", "timestamp", section=additional_info_section)
SUPPORTED_PYTHON_VERSIONS = MetaFeature(
    "Supported Python versions", "supported_python_version", section=additional_info_section
)
SUPPORTED_PLATFORMS = MetaFeature("Supported Platforms", "supported_platforms", section=additional_info_section)
NUMBER_DEPENDENCIES = MetaFeature(
    "Number of Installed Depenencies", "number_of_dependencies", section=additional_info_section
)
CODECOV_RESULT = MetaFeature("Codecov results", "reported_codecov_result", section=additional_info_section)
FAILING_TEST_INSIGHT = MetaFeature("Failing test jobs", "details_failing_tests", section=additional_info_section)
NUM_ANALYZED_PYFILES = MetaFeature("Number of analyzed Python files", "number_py_files", section=additional_info_section)
INSTALLABILITY_INSIGHT = MetaFeature("Installability issues", "installation_issues", section=additional_info_section)

# Checks
HAS_SUPPORT_WIN = MetaFeature("Has explicit Windows support", "has_windows_support", section=os_section)
HAS_SUPPORT_LINX = MetaFeature("Has explicit Linux support", "has_linux_support", section=os_section)
HAS_SUPPORT_MACOS = MetaFeature("Has explicit MacOS support", "has_macos_support", section=os_section)
INSTALLABLE_WIN = MetaFeature("Installable on Windows", "installable_windows", section=install_section)
INSTALLABLE_LINUX = MetaFeature("Installable on Linux", "installable_linux", section=install_section)
INSTALLABLE_MACOS = MetaFeature("Installable on MacOS", "installable_macos", section=install_section)
ALL_WHEELS_WIN = MetaFeature("All deps are wheels for Windows", "allwheel_windows", section=install_section)
ALL_WHEELS_LINUX = MetaFeature("All deps are wheels for Linux", "allwheel_linux", section=install_section)
ALL_WHEELS_MACOS = MetaFeature("All deps are wheels for MacOS", "allwheel_macos", section=install_section)
HAS_C_EXT_WIN = MetaFeature(
    "Has no deps with C extensions for Windows", "has_no_C_ext_windows", section=install_section)

HAS_C_EXT_LINUX = MetaFeature(
    "Has no deps with C extensions for Linux", "has_no_C_ext_linux", section=install_section)

HAS_C_EXT_MACOS = MetaFeature(
    "Has no deps with C extensions for MacOS", "has_no_C_ext_macos", section=install_section)

HAS_GITHUB_WORKFLOWS = MetaFeature("Github Action Workflows are configured", "exists", section=testing_section)
HAS_TESTS_WORKFLOWS = MetaFeature(
    "Github Action tests are configured", "gh_test_config", section=testing_section
)
HAS_CODECOV_WORKFLOWS = MetaFeature(
    "Github Action codecov is configured", "gh_codecov_config", section=testing_section
)
HAS_SUCCESS_TESTS = MetaFeature(
    "Tests are passing for main/master branch", "has_successful_tests", section=testing_section
)
HAS_CODE_COV_80 = MetaFeature(
    "Tests cover more than 80% of the code for main/master branch",
    "has_codecove_more_80", section=testing_section,
)
HAS_CODE_COV_RESULTS = MetaFeature(
    "Project has codecov result on main/master branch",
    "has_codecove_results", section=testing_section,
)
HAS_OSI_LICENSE = MetaFeature("Is licence OSI approved", "is_osi_approved", section=license_section)
NPE2_ERRORS = MetaFeature("Has no npe2 parsing errors", "has_no_npe_parse_errors", section=error_section)
CONDA_LINUX = MetaFeature("Linux bundle support", "is_linux_supported", section=conda_section)
CONDA_WIN = MetaFeature("Windows bundle support", "is_windows_supported", section=conda_section)
CONDA_MACOS = MetaFeature("MacOS bundle support", "is_macos_supported", section=conda_section)
HAD_UNKNOWN_ERROR = MetaFeature(
    "Had no unexpected error during dependency analysis", "had_no_unknown_error", section=error_section
)
HAS_LICENSE = MetaFeature("Has LICENSE file", "exists", section=license_section)
HAS_NO_PYQT_PYSIDE_DEP = MetaFeature(
    "Has no dependencies to PySide2 or PyQt5", "has_no_forbidden_deps", section=dependencies_section
)
HAS_NO_PYQT_PYSIDE_CODE = MetaFeature(
    "Has no code reference to PySide2 or PyQt5", "has_no_forbidden_imports", section=dependencies_section
)
IS_NPE2 = MetaFeature("Is NPE2 plugin", "is_npe2", section=npe_section)
IS_NOT_HYBRID = MetaFeature(
    "Is not hybrid (is NPE1 or NPE2, not both)", "is_not_hybrid", section=npe_section
)
HAS_NO_NPE1_HOOKS = MetaFeature("Has no NPE1 hook", "as_no_npe1_hook_list", section=npe_section)


def suite_generator(plugin_repo: NapariPlugin, disable_pip_based_requirements=False):
    if disable_pip_based_requirements:
        print("[yellow]WARNING! Pip based analysis are disabled[/yellow]")
        requirements = []
    else:
        requirements = [plugin_repo.requirements]

    npe2_yaml = plugin_repo.npe2_yaml
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
        print("[yellow]WARNING! GitHub actions based analysis are disabled (cannot identify an URL for your plugin)[/yellow]")
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
                features=[ENGINE_VERSION],
                main_files=[npe2_yaml],
                fallbacks=[],
            ),
            Requirement(
                features=[SUPPORTED_PLATFORMS, SUPPORTED_PYTHON_VERSIONS],
                main_files=[plugin_repo],
                fallbacks=[],
            ),
            Requirement(
                features=[NUMBER_DEPENDENCIES, INSTALLABILITY_INSIGHT],
                main_files=requirements,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[CODECOV_RESULT, FAILING_TEST_INSIGHT],
                main_files=main_gh_workfolder,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[NUM_ANALYZED_PYFILES],
                main_files=[linter],
                fallbacks=[],
            ),
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
                ],
                main_files=requirements,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[
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
                main_files=requirements,  # type: ignore
                fallbacks=[],
            ),
            Requirement(
                features=[HAS_NO_PYQT_PYSIDE_CODE],
                main_files=[linter],
                fallbacks=[],
            ),
            Requirement(
                features=[IS_NPE2],
                main_files=[npe2_yaml],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    IS_NOT_HYBRID,
                    HAS_NO_NPE1_HOOKS,
                ],
                main_files=[linter],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    NPE2_ERRORS,
                ],
                main_files=[condainfo],
                fallbacks=[],
            ),
            Requirement(
                features=[
                    HAD_UNKNOWN_ERROR,
                ],
                main_files=requirements,  # type: ignore
                fallbacks=[],
            ),
        ],
    )


project_quality_suite = (TITLE, suite_generator)
