import ast
from functools import wraps
from pathlib import Path
import time

from iguala import match
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
        if result.is_match:
            nodes = [
                (import_name, b["file"], b["ast_node"].lineno) for b in result.bindings
            ]
            return nodes
        return []

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
            if "/site-packages/" in str(python_file):
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