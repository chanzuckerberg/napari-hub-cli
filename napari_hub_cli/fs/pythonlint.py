import ast
from functools import wraps
from pathlib import Path

from iguala import as_matcher, match
from iguala import regex as re

from ..fs import RepositoryFile


class PythonFile(object):
    def __init__(self, path: Path):
        self.path = path
        self.strpath = str(path)
        if self.path.exists():
            self.ast = ast.parse(self.path.read_text("utf-8"))
        else:
            self.ast = None

    def _check_import(self, import_name):
        m = match(self.__class__)[
            "ast>*" : (
                match(ast.Import)["names>name" : re(import_name)]
                | match(ast.ImportFrom)["module" : re(import_name)]
            )
            @ "ast_node",
            "path":"@file",
        ]
        result = m.match(self)
        return self._extract_if_match(
            result, lambda b: (import_name, b["file"], b["ast_node"].lineno)
        )

    @classmethod
    def _extract_if_match(cls, result, extract_fun):
        if result.is_match:
            nodes = [extract_fun(b) for b in result.bindings]
            return nodes
        return []

    @property
    def npe1_import_hook_check(self):
        import_ = match(self.__class__)[
            "path":"@file",
            "ast>*" : (match(ast.Import)["names>name":"napari_plugin_engine"]),
            "ast>*" : (
                match(ast.FunctionDef)[
                    "decorator_list>*" : match(ast.Attribute)[
                        "value>id" : as_matcher("napari_plugin_engine")
                        @ "decorator_id",
                        "attr":"napari_hook_implementation",
                    ]
                ]
                @ "func"
            ),
        ]
        result = import_.match(self)
        return self._extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_import_hook_check(self):
        from_import_ = match(self.__class__)[
            "path":"@file",
            "ast>*" : (
                match(ast.ImportFrom)[
                    "module":"napari_plugin_engine",
                    "names" : match(ast.alias)[
                        "name" : as_matcher("napari_hook_implementation")
                        @ "decorator_id",
                        "asname":None,
                    ],
                ]
            ),
            "ast>*" : (
                match(ast.FunctionDef)["decorator_list>*>id":"@decorator_id",] @ "func"
            ),
        ]
        result = from_import_.match(self)
        return self._extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_import_as_hook_check(self):
        from_import_as_ = match(self.__class__)[
            "path":"@file",
            "ast>*" : (
                match(ast.ImportFrom)[
                    "module":"napari_plugin_engine",
                    "names" : match(ast.alias)[
                        "name":"napari_hook_implementation", "asname":"@decorator_id"
                    ],
                ]
            ),
            "ast>*" : (
                match(ast.FunctionDef)["decorator_list>*>id":"@decorator_id",] @ "func"
            ),
        ]
        result = from_import_as_.match(self)
        return self._extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def npe1_from_as_hook_check(self):
        from_as_ = match(self.__class__)[
            "path":"@file",
            "ast>*" : (
                match(ast.Import)[
                    "names" : match(ast.alias)[
                        "name":"napari_plugin_engine", "asname":"@decorator_id"
                    ],
                ]
            ),
            "ast>*" : (
                match(ast.FunctionDef)[
                    "decorator_list>*" : match(ast.Attribute)[
                        "value>id":"@decorator_id",
                        "attr":"napari_hook_implementation",
                    ],
                ]
                @ "func"
            ),
        ]
        result = from_as_.match(self)
        return self._extract_if_match(
            result, lambda b: (b["file"], b["func"].lineno, b["decorator_id"])
        )

    @property
    def check_pyside(self):
        return self._check_import("PySide2") + self._check_import("PySide6")

    @property
    def check_pyqt(self):
        return self._check_import("PyQt5") + self._check_import("PyQt6")


class PythonSrcDir(RepositoryFile):
    def __init__(self, path):
        super().__init__(path)
        files = []
        for python_file in self.file.glob("**/*.py"):
            if "site-packages" in str(python_file):
                # exclude virtualenv files
                continue
            files.append(PythonFile(python_file))
        self.files = files

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
