import logging
import sys
from pathlib import Path
from time import strftime

import pyqt5_fugueicons as fugue
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from lumed_tpm.tpm_control import Powermeter
from lumed_tpm.ui.tpm_ui import Ui_widgetTLabPowermeter

logger = logging.getLogger(__name__)

LOGS_DIR = Path.home() / "logs/IPS"
LOG_PATH = LOGS_DIR / f"{strftime('%Y_%m_%d_%H_%M_%S')}.log"

LASER_STATE = {0: "Idle", 1: "ON", 2: "Not connected"}

LOG_FORMAT = (
    "%(asctime)s - %(levelname)s"
    "(%(filename)s:%(funcName)s)"
    "(%(filename)s:%(lineno)d) - "
    "%(message)s"
)


def configure_logger():
    """Configures the logger if lumed_ips is launched as a module"""

    if not LOGS_DIR.parent.exists():
        LOGS_DIR.parent.mkdir()
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir()

    formatter = logging.Formatter(LOG_FORMAT)

    terminal_handler = logging.StreamHandler()
    terminal_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setFormatter(formatter)

    logger.addHandler(terminal_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)


class TLabPowermeterWidget(QWidget, Ui_widgetTLabPowermeter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # logger
        logger.info("Widget initialization")

        self.powermeter: Powermeter = Powermeter()

        # UI setup
        self.setup_default_ui()
        self.connect_ui_signals()
        self.setup_update_timer()
        self.update_ui()
        logger.info("Widget initialization complete")

    def setup_default_ui(self):
        self.pushButtonRefresh.setIcon(fugue.icon("magnifier-left"))

        self.spinBoxCounts.setMinimum(1)

    def connect_ui_signals(self):

        # Device
        self.pushButtonRefresh.clicked.connect(self.update_pm_list)
        self.pushButtonConnect.clicked.connect(self.connect_powermeter)
        self.pushButtonDisconnect.clicked.connect(self.disconnect_powermeter)

        # Settings
        self.comboBoxUnit.currentIndexChanged.connect(self.unit_changed)
        self.pushButtonAutoRange.clicked.connect(self.auto_range_toggled)
        self.doubleSpinBoxRange.valueChanged.connect(self.power_range_changed)
        self.spinBoxCounts.valueChanged.connect(self.average_count_changed)

        # Measurements
        self.pushButtonSingleMeasurement.clicked.connect(self.take_single_power)

    def setup_update_timer(self):
        self.update_timer = QTimer()
        self.update_timer.setInterval(100)
        self.update_timer.timeout.connect(self.update_ui)

    def update_ui(self):

        isconnected = self.powermeter.isconnected

        self.pushButtonConnect.setEnabled(not isconnected)

        self.pushButtonDisconnect.setEnabled(isconnected)
        self.groupBoxSettings.setEnabled(isconnected)
        self.groupBoxMeasurements.setEnabled(isconnected)
        self.groupBoxDetail.setEnabled(isconnected)

        if isconnected:
            try:
                self.update_settings()
                self.update_detail()
                self.update_measurements()
            except Exception as e:
                logger.error(e)
                self.disconnect_powermeter()

    def update_settings(self):

        if not self.comboBoxUnit.hasFocus():
            unit = self.powermeter.get_power_unit()
            index = {"W": 0, "DBM": 1}
            self.comboBoxUnit.setCurrentIndex(index[unit])

        if not self.pushButtonAutoRange.hasFocus():
            self.pushButtonAutoRange.setChecked(self.powermeter.get_auto_range())

        if self.pushButtonAutoRange.isChecked():
            self.pushButtonAutoRange.setText("Enabled")
            self.doubleSpinBoxRange.setEnabled(False)
        else:
            self.pushButtonAutoRange.setText("Disabled")
            self.doubleSpinBoxRange.setEnabled(True)

        if not self.doubleSpinBoxRange.hasFocus():
            current_range = float(self.powermeter.get_range())
            if current_range != self.doubleSpinBoxRange.value():
                self.doubleSpinBoxRange.setValue(current_range)

        if not self.spinBoxCounts.hasFocus():
            self.spinBoxCounts.setValue(self.powermeter.get_average_count())

    def update_detail(self):
        self.lineEditModel.setText(self.powermeter._model)
        self.lineEditSerialNumber.setText(self.powermeter._serial_number)
        self.lineEditFirmwareVersion.setText(self.powermeter._firmware_version)

    def update_measurements(self):
        pass

    # Device

    def update_pm_list(self):
        logger.info("looking for connected powermeters")
        available_pm = self.powermeter.find_thorlabs_pm()

        self.comboBoxDevice.clear()
        self.comboBoxDevice.addItems(available_pm)

    def connect_powermeter(self):
        device = self.comboBoxDevice.currentText()

        try:
            logger.info("connecting powermeter %s", device)
            self.powermeter.connect(device)
            self.apply_default()
            self.update_ui()
            self.update_timer.start()

        except Exception as e:
            logger.error(e)

    def disconnect_powermeter(self):
        if not self.powermeter.isconnected:
            logger.error("powermeter not connected")
            return

        logger.info("Disconnecting powermeter")
        self.powermeter.disconnect()
        self.update_timer.stop()
        self.update_ui()

    def apply_default(self):

        if not self.powermeter.isconnected:
            logger.error("powermeter not connected")
            return

        self.powermeter.set_correction_wavelength(785)
        self.powermeter.set_power_unit("W")
        self.powermeter.set_auto_range(False)
        self.powermeter.set_range(50e-3)
        self.powermeter.set_average_count(1)

    # Settings
    def unit_changed(self):
        new_units = ["W", "DBM"][self.comboBoxUnit.currentIndex()]

        try:
            self.powermeter.set_power_unit(new_units)
            logger.info("power units changed to %s", new_units)
        except Exception as e:
            logger.error(e)

    def auto_range_toggled(self):
        autorange_enabled = self.pushButtonAutoRange.isChecked()

        try:
            self.powermeter.set_auto_range(autorange_enabled)
            logger.info("auto range enabled : %s", autorange_enabled)
        except Exception as e:
            logger.error(e)

    def power_range_changed(self):
        new_range = self.doubleSpinBoxRange.value()

        try:
            self.powermeter.set_range(new_range)
            logger.info("power range changed to %s", new_range)
        except Exception as e:
            logger.error(e)

    def average_count_changed(self):
        average_count = self.spinBoxCounts.value()

        try:
            self.powermeter.set_average_count(average_count)
            logger.info("average count number set to %s", average_count)
        except Exception as e:
            logger.error(e)

    # Measurements

    def take_single_power(self):
        power = self.powermeter.get_power()
        units = self.powermeter.get_power_unit()

        self.lineEditPower.setText(f"{power:.2e}")
        self.labelPowerUnits.setText(units)


if __name__ == "__main__":
    # Set up logging
    configure_logger()

    # Create app window
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()

    window.setCentralWidget(TLabPowermeterWidget())

    app.exec_()
