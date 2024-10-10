import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from lumed_tpm.tpm_widget import TLabPowermeterWidget, configure_logger

if __name__ == "__main__":
    # Set up logging
    configure_logger()

    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    window.setCentralWidget(TLabPowermeterWidget())

    app.exec_()
