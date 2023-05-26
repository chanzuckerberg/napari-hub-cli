from pathlib import Path
import pytest
from napari_hub_cli.fs.pythonlint import PythonFile



@pytest.fixture(scope="module")
def resources():
    return Path(__file__).parent.absolute() / "resources" / "python"


def test_pythonfile_init(resources):
    srcfile = PythonFile(resources / "f1.py")

    assert srcfile.ast


def test_pythonfile_pyside2_detection(resources):
    srcfile = PythonFile(resources / "f1.py")

    res = srcfile.check_pyside2
    assert res == [('PySide2', srcfile.path, 2),
                   ('PySide2', srcfile.path, 24),
                   ('PySide2', srcfile.path, 25)]
    assert srcfile.check_pyqt5 == []


def test_pythonfile_pyqt5_detection(resources):
    srcfile = PythonFile(resources / "f2.py")

    res = srcfile.check_pyqt5
    assert res == [('PyQt5', srcfile.path, 1),
                   ('PyQt5', srcfile.path, 17),
                   ('PyQt5', srcfile.path, 18)]
    assert srcfile.check_pyside2 == []