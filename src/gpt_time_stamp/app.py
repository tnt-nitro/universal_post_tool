import sys
import os
from PySide6.QtWidgets import QApplication
from gpt_time_stamp.ui.main_window import MainWindow

# DPI-Awareness Warnung unterdrücken (optional)
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
