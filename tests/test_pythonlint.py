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
        ("PySide2", srcfile.path, 25),
        ("PySide2", srcfile.path, 26),
    ]
    assert srcfile.check_pyqt5 == []


def test_pythonfile_pyqt5_detection(resources):
    srcfile = PythonFile(resources / "f2.py")

    res = srcfile.check_pyqt5
    assert res == [
        ("PyQt5", srcfile.path, 3),
        ("PyQt5", srcfile.path, 18),
        ("PyQt5", srcfile.path, 19),
    ]
    assert srcfile.check_pyside2 == []


def test_pythonfile_npe1_hook_check1(resources):
    srcfile = PythonFile(resources / "f1.py")

    res = srcfile.npe1_import_hook_check
    assert res != []
    assert res == [
        (srcfile.path, 38, "napari_plugin_engine")
    ]

    res = srcfile.npe1_from_import_hook_check
    assert res != []
    assert res == [
        (srcfile.path, 30, "napari_hook_implementation")
    ]

    srcfile = PythonFile(resources / "f2.py")
    res = srcfile.npe1_import_hook_check
    assert res == []

    res = srcfile.npe1_from_import_hook_check
    assert res == []


def test_pythonfile_npe1_hook_check2(resources):
    srcfile = PythonFile(resources / "f2.py")

    res = srcfile.npe1_from_import_as_hook_check
    assert res != []
    assert res == [
        (srcfile.path, 23, "nhi")
    ]

    srcfile = PythonFile(resources / "f1.py")
    res = srcfile.npe1_from_import_as_hook_check
    assert res == []


def test_pythonfile_npe1_hook_check3(resources):
    srcfile = PythonFile(resources / "subdir" / "f1.py")

    res = srcfile.npe1_from_as_hook_check
    assert res != []
    assert res == [
        (srcfile.path, 14, "npe")
    ]

    srcfile = PythonFile(resources / "f1.py")
    res = srcfile.npe1_from_as_hook_check
    assert res == []


def test_pythonsrcdir_init(resources):
    srcdir = PythonSrcDir(resources)

    assert srcdir.number_py_files == 3


def test_pythonsrcdir_forbidden_imports_detection(resources):
    srcdir = PythonSrcDir(resources)

    res = srcdir.forbidden_imports_list

    assert len(res) == 6
    assert res == [
        ("PySide2", srcdir.files[0].path, 3),
        ("PySide2", srcdir.files[0].path, 25),
        ("PySide2", srcdir.files[0].path, 26),
        ("PyQt5", srcdir.files[1].path, 3),
        ("PyQt5", srcdir.files[1].path, 18),
        ("PyQt5", srcdir.files[1].path, 19),
    ]
    assert srcdir.has_no_forbidden_imports is False
    assert srcdir.number_py_files == 3


def test_pythonsrcdir_forbidden_imports_detection2(resources):
    srcdir = PythonSrcDir(resources / "subdir")

    res = srcdir.forbidden_imports_list

    assert res == []
    assert srcdir.has_no_forbidden_imports is True
    assert srcdir.number_py_files == 1


def test_pythonsrcdir_npe1_hook_list(resources):
    srcdir = PythonSrcDir(resources)

    res = srcdir.npe1_hook_list

    assert res != []
    assert srcdir.as_no_npe1_hook_list is False
    assert res == [
        (srcdir.files[0].path, 38, "napari_plugin_engine"),
        (srcdir.files[0].path, 30, "napari_hook_implementation"),
        (srcdir.files[1].path, 23, "nhi"),
        (srcdir.files[2].path, 14, "npe")
    ]