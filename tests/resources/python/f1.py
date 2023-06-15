import sys

from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton

from napari_plugin_engine import napari_hook_implementation


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("My Form")


if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form()
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())


def inner():
    def inner2():
        import PySide2.QtWidgets
        from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton


@napari_hook_implementation(firstresult=True)
def napari_get_reader(path):
    ...


import napari_plugin_engine


@napari_plugin_engine.napari_hook_implementation(stuff=False)
def napari_get_reader(path):
    ...
