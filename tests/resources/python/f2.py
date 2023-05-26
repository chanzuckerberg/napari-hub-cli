from PyQt5.QtWidgets import QApplication, QWidget
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.resize(300,300)
    w.setWindowTitle("Guru99")
    w.show()
    sys.exit(app.exec_())



def inner():
    def inner2():
        from PyQt5.QtWidgets import QApplication, QWidget
        import PyQt5.QtWidgets