from functools import lru_cache
from gettext import install
from itertools import product
from pathlib import Path

from pip._internal.exceptions import DistributionNotFound, InstallationError

from .solver import DependencySolver
from .utils import build_options

accepted_C_packages = {
    "numpy",
    "pandas",
}


class InstallationRequirements(object):
    def __init__(self, path, requirements, python_versions=None, platforms=None):
        # self.plugin = plugin
        self.solver = DependencySolver("solver", "")
        self.requirements = requirements
        self.path = path
        self.python_versions = python_versions if python_versions else [None]
        self.platforms = platforms if platforms else [None]
        # self.requirements = self.plugin.extractfrom_config("requirements")
        if self.requirements is None:
            try:
                with self.path.open(encoding="utf-8"):
                    content = self.path.read_text()
                self.requirements = content.splitlines()
            except Exception:
                self.requirements = []
        self.options_list = self._build_options()

    def _build_options(self):
        # Read the classifiers to have python's versions and platforms
        python_versions = self.python_versions
        platforms = self.platforms
        options_list = []
        for python_version, platform in product(python_versions, platforms):
            options = build_options(python_version, platform)
            options.named_platform = platform
            options_list.append(options)
        return options_list

    @lru_cache()
    def solve_dependencies(self, options):
        try:
            return self.solver.solve_dependencies(self.requirements, options)
        except DistributionNotFound:
            return None

    @lru_cache()
    def _get_platform_options(self, platform):
        options_platform = []
        for options in self.options_list:
            if platform in options.named_platform:
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

    def has_C_extensions_dependencies(self, options):
        _, _, c_exts, _ = self.analysis_package(options)
        return len(set(c_exts) - accepted_C_packages) > 0

    def alldeps_wheel(self, options):
        _, all_wheels, _, _ = self.analysis_package(options)
        return all_wheels

    def is_installable(self, options):
        installable, _, _, _ = self.analysis_package(options)
        return installable

    def _isfor_platform(self, platform, result_index):
        for options in self._get_platform_options(platform):
            res = self.analysis_package(options)[result_index]
            if not res:
                return False
        return True

    @property
    def installable_windows(self):
        return self._isfor_platform("win", 0)

    @property
    def installable_linux(self):
        return self._isfor_platform("linux", 0)

    @property
    def installable_macos(self):
        return self._isfor_platform("macos", 0)

    @property
    def allwheel_windows(self):
        return self._isfor_platform("win", 1)

    @property
    def allwheel_linux(self):
        return self._isfor_platform("linux", 1)

    @property
    def allwheel_macos(self):
        return self._isfor_platform("macos", 1)

    @property
    def has_C_ext_windows(self):
        for options in self._get_platform_options("win"):
            res = self.has_C_extensions_dependencies(options)
            if res:
                return True
        return False

    @property
    def has_C_ext_linux(self):
        for options in self._get_platform_options("linux"):
            res = self.has_C_extensions_dependencies(options)
            if res:
                return True
        return False

    @property
    def has_C_ext_macos(self):
        for options in self._get_platform_options("macos"):
            res = self.has_C_extensions_dependencies(options)
            if res:
                return True
        return False
