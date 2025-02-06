import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from logging_config import configure_logging


def main():
    configure_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
