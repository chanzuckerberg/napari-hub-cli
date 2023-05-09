from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement, RequirementSuite

TITLE = "Code Quality"

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
HAS_OSI_LICENSE = MetaFeature("Is licence OSI approved", "is_osi_approved")
NPE2_ERRORS = MetaFeature("Has npe2 parsing errors", "has_npe_parse_errors")
CONDA_LINUX = MetaFeature("Linux bundle support", "is_linux_supported")
CONDA_WIN = MetaFeature("Windows bundle support", "is_windows_supported")
CONDA_MACOS = MetaFeature("MacOS bundle support", "is_macos_supported")
HAD_UNKNOWN_ERROR = MetaFeature("Had no unexpected error during dependency analysis", "had_no_unknown_error")
HAS_LICENSE = MetaFeature("Has LICENSE file", "exists")


def suite_generator(plugin_repo: NapariPlugin):
    requirements = plugin_repo.requirements
    condainfo = plugin_repo.condainfo
    license = plugin_repo.license
    return RequirementSuite(
        title=TITLE,
        requirements=[
            Requirement(
                features=[HAS_OSI_LICENSE],
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
                main_files=[requirements],
                fallbacks=[],
            ),
        ],
    )


project_quality_suite = (TITLE, suite_generator)
