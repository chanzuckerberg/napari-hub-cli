import sys

from PyQt5.QtWidgets import QApplication, QWidget
from napari_plugin_engine import napari_hook_implementation as nhi


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(300, 300)
    w.setWindowTitle("Guru99")
    w.show()
    sys.exit(app.exec_())


def inner():
    def inner2():
        import PyQt5.QtWidgets
        from PyQt5.QtWidgets import QApplication, QWidget


@nhi(specname="napari_get_reader")
def whatever_name_you_want(path: str):
    ...
