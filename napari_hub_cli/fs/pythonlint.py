from .patch_parso import *

import parso
from parso.python import tree as ast

from pathlib import Path

from iguala import match, regex as re, is_not

from ..utils import extract_if_match

from ..fs import RepositoryFile


class PythonFile(object):
    def __init__(self, path: Path):
        self.path = path
        self.strpath = str(path)
        if self.path.exists():
            txt = self.path.read_text("utf-8")
            try:
                self.ast = parso.parse(txt, path=str(self.path), version="3.11")
            except UnicodeDecodeError:
                self.ast = None
        else:
            self.ast = None

    def _check_import(self, import_name):
        m = match(self.__class__)[
            "ast>body+" : (
                match(ast.ImportName)["names>value" : re(import_name)]
                | match(ast.ImportFrom)["module" : re(import_name)]
            )
            @ "ast_node",
            "path":"@file",
        ]
        result = m.match(self)
        return extract_if_match(
            result, lambda b: (import_name, b["file"], b["ast_node"].lineno)
        )

    @property
    def npe1_import_hook_check(self):
        import_ = match(self.__class__)[
            "path":"@file",
            "ast>body+" : (match(ast.ImportName)["names>value":"napari_plugin_engine"]),
            "ast>body+" : (
                match(ast.Function)[
                    "decorator_names" : re(
                        r"napari_plugin_engine\.napari_hook_implementation"
                    )
                    @ "decorator_id"
                ]
                @ "func"
            ),
        ]
        result = import_.match(self)
        return extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_import_hook_check(self):
        from_import_ = match(self.__class__)[
            "path":"@file",
            "ast>body+" : (
                match(ast.ImportFrom)[
                    "module":"napari_plugin_engine",
                    "alias":"napari_hook_implementation",
                ]
            ),
            "ast>body+" : (
                match(ast.Function)[
                    "decorator_names" : re("napari_hook_implementation")
                    @ "decorator_id"
                ]
                @ "func"
            ),
        ]
        result = from_import_.match(self)
        return extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_import_as_hook_check(self):
        from_import_as_ = match(self.__class__)[
            "path":"@file",
            "ast>body+" : (
                match(ast.ImportFrom)[
                    "module":"napari_plugin_engine",
                    "names>value" : re("napari_hook_implementation"),
                    "alias":"@decorator_id",
                    "alias" : is_not("napari_hook_implementation"),
                ]
            ),
            "ast>body+" : (
                match(ast.Function)["decorators>body>value":"@decorator_id"] @ "func"
            ),
        ]
        result = from_import_as_.match(self)
        return extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_as_hook_check(self):
        from_as_ = match(self.__class__)[
            "path":"@file",
            "ast>body+" : (
                match(ast.ImportName)[
                    "names>value":"napari_plugin_engine",
                    "alias":"@decorator_id",
                    "alias" : is_not("napari_plugin_engine"),
                ]
            ),
            "ast>body+" : (
                match(ast.Function)["decorators>body>value":"@decorator_id"] @ "func"
            ),
        ]
        result = from_as_.match(self)
        return extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def check_pyside(self):
        return self._check_import("PySide2") + self._check_import("PySide6")

    @property
    def check_pyqt(self):
        return self._check_import("PyQt5") + self._check_import("PyQt6")


class PythonSrcDir(RepositoryFile):
    def __init__(self, path, engine_version=None, exclude_test_folders=True):
        super().__init__(path)
        files = []
        for python_file in self.file.glob("**/*.py"):
            if "site-packages" in str(python_file) or (
                exclude_test_folders and "tests" in str(python_file)
            ):
                # exclude virtualenv files and tests
                continue
            files.append(PythonFile(python_file))
        self.files = files
        self.engine_version = engine_version
        self.exclude_test_folders = exclude_test_folders

    @property
    def forbidden_imports_list(self):
        imports = []
        for file in self.files:
            imports.extend(file.check_pyside)
            imports.extend(file.check_pyqt)
        return imports

    @property
    def has_no_forbidden_imports(self):
        return len(self.forbidden_imports_list) == 0

    @property
    def number_py_files(self):
        return len(self.files)

    @property
    def npe1_hook_list(self):
        hooks = []
        for file in self.files:
            hooks.extend(file.npe1_import_hook_check)
            hooks.extend(file.npe1_from_import_hook_check)
            hooks.extend(file.npe1_from_import_as_hook_check)
            hooks.extend(file.npe1_from_as_hook_check)
        return hooks

    @property
    def as_no_npe1_hook_list(self):
        return len(self.npe1_hook_list) == 0

    @property
    def is_not_hybrid(self):
        return (not self.as_no_npe1_hook_list) ^ (self.engine_version == 2)
