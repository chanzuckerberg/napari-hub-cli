import sys

from PyQt5.QtWidgets import QApplication, QWidget

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
