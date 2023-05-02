from functools import lru_cache
from itertools import product
from pathlib import Path

from .solver import DependencySolver
from .utils import build_options


class InstallationRequirements(object):
    def __init__(self, plugin):
        self.plugin = plugin
        self.solver = DependencySolver("solver", "")
        self.options_list = self._build_options()
        self.requirements = self.plugin.extractfrom_config("requirements")
        if self.requirements is None:
            try:
                file = self.plugin.path / "requirements.txt"
                with file.open(encoding="utf-8"):
                    content = file.read_text()
                self.requirements = content.splitlines()
            except Exception:
                self.requirements = []


    def _build_options(self):
        # Read the classifiers to have python's versions and platforms
        python_versions = self.plugin.supported_python_version
        platforms = self.plugin.supported_platforms
        options_list = []
        for python_version, platform in product(python_versions, platforms):
            options = build_options(python_version, platform)
            options_list.append(options)
        return options_list

    @lru_cache()
    def solve_dependencies(self, options_index):
        # We consider that the folder path is actually the package name
        package_name = self.plugin.path.name
        try:
            return self.solver.solve_dependencies(
                package_name, self.options_list[options_index]
            )
        except Exception:
            return None

    # @property
    # def exists_in_pypi(self):
    #     requests.get()

    # def alldeps_are_wheels(self, platforms):
    #     probable_C = []
    #     for name, x in res.mapping.items():
    #         print(name, x.version)
    #         print(x)
    #         link = x.source_link
    #         if not link:
    #             print("remove", x)
    #             continue
    #         print("is wheel?", link.is_wheel)
    #         has_C = "none-any." not in link.filename
    #         if has_C:
    #             probable_C.append(name)
    #         print("contains C extension?", "!probable!" if has_C else "no(?)")
    #         print()

    #     print("Would install", len(res.mapping), "dependencies")
    #     print("There is", len(probable_C), "probable package with C extensions")
    #     print(probable_C)


# probable_C = []
# for name, x in res.mapping.items():
#     print(name, x.version)
#     print(x)
#     link = x.source_link
#     if not link:
#         print("remove", x)
#         continue
#     print("is wheel?", link.is_wheel)
#     has_C = "none-any." not in link.filename
#     if has_C:
#         probable_C.append(name)
#     print("contains C extension?", "!probable!" if has_C else "no(?)")
#     print()

# print("Would install", len(res.mapping), "dependencies")
# print("There is", len(probable_C), "probable package with C extensions")
# print(probable_C)
