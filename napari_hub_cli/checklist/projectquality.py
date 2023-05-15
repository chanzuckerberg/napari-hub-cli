from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement

HAS_SUPPORT_WIN = MetaFeature("Has explicit Windows support", "has_windows_support")
HAS_SUPPORT_LINX = MetaFeature("Has explicit Linux support", "has_windows_support")
HAS_SUPPORT_MACOS = MetaFeature("Has explicit MacOS support", "has_windows_support")
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
    "Tests cover more than 80% of the code", "has_codecove_more_80"
)
HAS_OSI_LICENSE = MetaFeature("Is licence OSI approved", "is_osi_approved")
NPE2_ERRORS = MetaFeature("Has npe2 parsing errors", "has_npe_parse_errors")
CONDA_LINUX = MetaFeature("Linux bundle support", "is_linux_supported")
CONDA_WIN = MetaFeature("Windows bundle support", "is_windows_supported")
CONDA_MACOS = MetaFeature("MacOS bundle support", "is_macos_supported")
HAD_UNKNOWN_ERROR = MetaFeature(
    "Had no unexpected error during dependency analysis", "had_no_unknown_error"
)
HAS_LICENSE = MetaFeature("Has LICENSE file", "exists")


def project_quality_suite(plugin_repo: NapariPlugin):
    requirements = plugin_repo.requirements
    condainfo = plugin_repo.condainfo
    license = plugin_repo.license
    gh_workflow_folder = plugin_repo.gh_workflow_folder
    if gh_workflow_folder.url is None:
        # if there is no url, we cannot query github
        main_gh_workfolder = []
    else:
        main_gh_workfolder = [gh_workflow_folder]

    return [
        Requirement(
            features=[HAS_LICENSE, HAS_OSI_LICENSE],
            main_files=[license],
            fallbacks=[],
        ),
        Requirement(
            features=[
                HAD_UNKNOWN_ERROR,
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
                HAS_CODE_COV_80,
            ],
            main_files=main_gh_workfolder,  # type: ignore
            fallbacks=[],
        ),
    ]
