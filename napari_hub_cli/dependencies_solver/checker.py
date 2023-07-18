from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
import sys

# This hack is here to remove a warning message that is yield by "_distutils_hack"
with suppress(ImportError):
    import sys

    def hack_clear_distutils():
        if "distutils" not in sys.modules:
            return  # pragma: no cover
        mods = [
            name
            for name in sys.modules
            if name == "distutils" or name.startswith("distutils.")
        ]
        for name in mods:
            del sys.modules[name]

    import _distutils_hack as hack

    hack.clear_distutils = hack_clear_distutils


from .pip_patch import *  # This import needs to be imported just after the distutils hack and before any "pip" related import

from functools import lru_cache
from itertools import product

from pip._internal.exceptions import DistributionNotFound, InstallationSubprocessError, MetadataGenerationFailed, InstallationError

from ..fs import ConfigFile
from .solver import DependencySolver
from .utils import build_options

accepted_C_packages = {
    "numpy",
    "pandas",
}

forbidden_deps = {
    "pyside",
    "pyside2",
    "pyside6",
    "pyqt",
    "pyqt5",
    "pyqt6",
}

INSTALLABLE = 0
ALL_WHEELS = 1
PROBABLE_C_DEPS = 2
DEPENDENCIES = 3

NO_DEPENDENCIES = "Failed to resolve dependencies"


def dirty_threadpool(f):
    def inner(self):
        self._analyse_with_all_options()
        return f(self)

    return inner


class InstallationRequirements(ConfigFile):
    def __init__(
        self,
        path,
        requirements,
        python_versions=None,
        platforms=("win", "linux", "macos"),
    ):
        super().__init__(path)
        self.solver = DependencySolver("solver", "")
        self.requirements = requirements
        self.python_versions = python_versions if python_versions else [None]
        self.platforms = platforms if platforms else [None]
        if not self.requirements:
            self.requirements = self.data.get("content", "").splitlines()
        self.options_list = self._build_options()
        self.errors = {}
        self._installation_issues = {}

    def _build_options(self):
        # Read the classifiers to have python's versions and platforms
        python_versions = self.python_versions
        platforms = self.platforms
        options_list = []
        for python_version, platform in product(python_versions, platforms):
            options = build_options(python_version, platform)
            options.named_platform = platform if platform else {"win", "linux", "macos"}
            options_list.append(options)
        return options_list

    @lru_cache()
    def solve_dependencies(self, options):
        try:
            return self.solver.solve_dependencies(self.requirements, options)
        except DistributionNotFound as e:
            # print("Distribution not found", e, options.python_version, options.platforms)
            message = f"A direct or transitive dependency cannot be resolve: {e.args[0]}"
            kind = "dependency distribution not found"
        except MetadataGenerationFailed as e:
            message = f"An error occured while building one of the dependencies that doesn't have wheel: {e.context}"
            kind = "dependency has no wheel"
        except InstallationSubprocessError as e:
            message = f"An error occured in a sub-process: {e.args[0]}"
            kind = "sub-process/package build error"
            # print("SubProcessError", e, options.python_version, options.platforms)
        except InstallationError as e:
            message = f"An error occured while installing this dependency (could be the need for dev tools to build it): {getattr(e, 'project', '')}"
            kind = "dependency need dev tools"
        except Exception as e:
            # print("General Exception", e, options.python_version, options.platforms)
            self.errors[options] = e
            return None

        # Build the information message
        platform = options.platforms[0]
        if "linux" in platform:
            platform = "linux"
        elif "macos" in platform:
            platform = "macos"
        else:
            platform = "windows"

        version = options.python_version
        if version is None or len(version) == 0:
            major, minor, *_ = sys.version_info
            version = (major, minor)
        version = ".".join(str(x) for x in version)
        self._installation_issues[(version, platform)] = (message, kind)
        return None

    @lru_cache()
    def _get_platform_options(self, platform):
        options_platform = []
        for options in self.options_list:
            if options.named_platform and platform in options.named_platform:
                options_platform.append(options)
        return options_platform

    @lru_cache()
    def analysis_package(self, options):
        result = self.solve_dependencies(options)
        if result is None:
            return False, True, [], []
        all_wheels = True
        probable_C = []
        installed = []
        for name, x in result.mapping.items():
            link = x.source_link
            if not link:
                continue
            all_wheels = all_wheels and link.is_wheel
            has_C = "none-any." not in link.filename
            if has_C:
                probable_C.append(name)
            installed.append((name, x.version))
        return True, all_wheels, probable_C, installed

    def num_installed_packages(self, options):
        _, _, _, installed = self.analysis_package(options)
        return len(installed)

    def has_no_C_extensions_dependencies(self, options):
        _, _, c_exts, _ = self.analysis_package(options)
        return len(set(c_exts) - accepted_C_packages) == 0

    def alldeps_wheel(self, options):
        _, all_wheels, _, _ = self.analysis_package(options)
        return all_wheels

    def is_installable(self, options):
        installable, _, _, _ = self.analysis_package(options)
        return installable

    def _isfor_platform(self, platform, result_field_index):
        options_list = self._get_platform_options(platform)
        if not options_list:
            return False  # pragma: no cover
        for options in options_list:
            res = self.analysis_package(options)[result_field_index]
            if not res:
                return False  # pragma: no cover
        return True

    # lru cache here is a dirty trick to ensure that this function will be called only once
    # but this only works if all the methods that will call it using the dirty decorator
    # are called sequentially.
    # if the methods with the dirty decorator are called in parallel, it's mandatory to
    # use a lock on an instance variable to know if this function has been started already or not
    @lru_cache()
    def _analyse_with_all_options(self):
        with ThreadPoolExecutor(max_workers=len(self.options_list)) as executor:
            executor.map(self.analysis_package, self.options_list)
        for tmp_dir in global_tracker:
            tmp_dir.cleanup()

    @property
    @dirty_threadpool
    def can_resolve_dependencies_linux(self):
        return self._isfor_platform("linux", DEPENDENCIES)

    @property
    @dirty_threadpool
    def can_resolve_dependencies_windows(self):
        return self._isfor_platform("win", DEPENDENCIES)

    @property
    @dirty_threadpool
    def can_resolve_dependencies_macos(self):
        return self._isfor_platform("macos", DEPENDENCIES)

    @property
    @dirty_threadpool
    def number_of_dependencies(self):
        result = max(self.num_installed_packages(o) for o in self.options_list)
        return NO_DEPENDENCIES if not result else result

    @property
    @dirty_threadpool
    def installable_windows(self):
        return self._isfor_platform("win", INSTALLABLE)

    @property
    @dirty_threadpool
    def installable_linux(self):
        return self._isfor_platform("linux", INSTALLABLE)

    @property
    @dirty_threadpool
    def installable_macos(self):
        return self._isfor_platform("macos", INSTALLABLE)

    @property
    @dirty_threadpool
    def allwheel_windows(self):
        return self.can_resolve_dependencies_windows and self._isfor_platform(
            "win", ALL_WHEELS
        )

    @property
    @dirty_threadpool
    def allwheel_linux(self):
        return self.can_resolve_dependencies_linux and self._isfor_platform(
            "linux", ALL_WHEELS
        )

    @property
    @dirty_threadpool
    def allwheel_macos(self):
        return self.can_resolve_dependencies_macos and self._isfor_platform(
            "macos", ALL_WHEELS
        )

    @property
    @dirty_threadpool
    def has_no_C_ext_windows(self):
        for options in self._get_platform_options("win"):
            res = self.has_no_C_extensions_dependencies(options)
            if not res:
                return False
        return self.can_resolve_dependencies_windows

    @property
    @dirty_threadpool
    def has_no_C_ext_linux(self):
        for options in self._get_platform_options("linux"):
            res = self.has_no_C_extensions_dependencies(options)
            if not res:
                return False
        return self.can_resolve_dependencies_linux

    @property
    @dirty_threadpool
    def has_no_C_ext_macos(self):
        for options in self._get_platform_options("macos"):
            res = self.has_no_C_extensions_dependencies(options)
            if not res:
                return False
        return self.can_resolve_dependencies_macos

    @property
    def has_windows_support(self):
        return "win" in self.platforms

    @property
    def has_linux_support(self):
        return "linux" in self.platforms

    @property
    def has_macos_support(self):
        return "macos" in self.platforms

    @property
    def had_no_unknown_error(self):
        return len(self.errors) == 0

    @property
    def has_no_forbidden_deps(self):
        _, _, _, deps = self.analysis_package(self.options_list[0])
        return all(name.lower() not in forbidden_deps for name, _ in deps)

    @property
    def installation_issues(self):
        information = ""
        for (pyv, platform), (reason, _) in self._installation_issues.items():
            information += f"\n   * {platform} - {pyv}: {reason}"
        return information if information else "No information"

    @property
    def installation_issues_summary(self):
        information = ""
        for (pyv, platform), (_, kind) in self._installation_issues.items():
            information += f"\n   * {platform} - {pyv}: {kind}"
        return information if information else "No issue"