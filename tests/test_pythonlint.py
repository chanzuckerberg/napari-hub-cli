from pathlib import Path

import pytest

from napari_hub_cli.fs.pythonlint import PythonFile, PythonSrcDir


@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources" / "python"


def test_pythonfile_init(resources):
    srcfile = PythonFile(resources / "f1.py")

    assert srcfile.ast


    srcfile = PythonFile(resources / "f5.py")

    assert srcfile.ast is None


def test_pythonfile_pyside2_detection(resources):
    srcfile = PythonFile(resources / "f1.py")

    res = srcfile.check_pyside2
    assert res == [
        ("PySide2", srcfile.path, 3),
        ("PySide2", srcfile.path, 24),
        ("PySide2", srcfile.path, 25),
    ]
    assert srcfile.check_pyqt5 == []


def test_pythonfile_pyqt5_detection(resources):
    srcfile = PythonFile(resources / "f2.py")

    res = srcfile.check_pyqt5
    assert res == [
        ("PyQt5", srcfile.path, 3),
        ("PyQt5", srcfile.path, 16),
        ("PyQt5", srcfile.path, 17),
    ]
    assert srcfile.check_pyside2 == []


def test_pythonsrcdir_init(resources):
    srcdir = PythonSrcDir(resources)

    assert srcdir.number_py_files == 3


def test_pythonsrcdir_forbidden_imports_detection(resources):
    srcdir = PythonSrcDir(resources)

    res = srcdir.forbidden_imports_list

    assert len(res) == 6
    assert res == [
        ("PySide2", srcdir.files[0].path, 3),
        ("PySide2", srcdir.files[0].path, 24),
        ("PySide2", srcdir.files[0].path, 25),
        ("PyQt5", srcdir.files[1].path, 3),
        ("PyQt5", srcdir.files[1].path, 16),
        ("PyQt5", srcdir.files[1].path, 17),
    ]
    assert srcdir.has_no_forbidden_imports is False
    assert srcdir.number_py_files == 3


def test_pythonsrcdir_forbidden_imports_detection2(resources):
    srcdir = PythonSrcDir(resources / "subdir")

    res = srcdir.forbidden_imports_list

    assert res == []
    assert srcdir.has_no_forbidden_imports is True
    assert srcdir.number_py_files == 1