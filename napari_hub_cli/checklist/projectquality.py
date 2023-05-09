from ..fs import NapariPlugin
from .metadata import MetaFeature, Requirement

NODOC = ""

HAS_SUPPORT_WIN = MetaFeature("Has explicit Windows support", "has_windows_support")
HAS_SUPPORT_LINX = MetaFeature("Has explicit Linux support", "has_windows_support")
HAS_SUPPORT_MACOS = MetaFeature("Has explicit MacOS support", "has_windows_support")
INSTALLABLE_WIN = MetaFeature("Installable on windows", "installable_windows")
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


def project_quality_suite(plugin_repo: NapariPlugin):
    requirements = plugin_repo.requirements
    license = plugin_repo.license
    return [
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
    ]
