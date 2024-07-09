from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import (
    QRunnable,
    QObject,
    QThread,
    pyqtSlot,
    QThreadPool,
    pyqtSignal,
    Qt,
)
import pyqtgraph as pg

from powermeter import Powermeter
from plots import PlotWindow


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `str` Exception string

    result
        `tuple` Data returned when processing is finished

    progress
        `object` Data returned while processing

    """

    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(object, object)


class MeasurePowerWorker(QRunnable):
    def __init__(self, pm: Powermeter):
        super().__init__()
        self.signals = WorkerSignals()
        self.pm = pm

    @pyqtSlot()
    def run(self):
        try:
            while self.pm.connected:
                power, power_units = self.pm.power
                self.signals.progress.emit(power, power_units)
                QThread.msleep(500)  # Refresh rate
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()


class Worker(QRunnable):
    def __init__(self, func=None, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        try:
            if self.func:
                result = self.func(*self.args, **self.kwargs)
            else:
                result = None, ""
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()
            self.signals.result.emit(result)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(490, 150)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.refreshRateLabel = QtWidgets.QLabel(self.centralwidget)
        self.refreshRateLabel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.refreshRateLabel.setObjectName("refreshRateLabel")
        self.horizontalLayout_3.addWidget(self.refreshRateLabel)
        self.refreshRateTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.refreshRateTextEdit.setMinimumSize(QtCore.QSize(0, 23))
        self.refreshRateTextEdit.setMaximumSize(QtCore.QSize(16777215, 23))
        self.refreshRateTextEdit.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.refreshRateTextEdit.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.refreshRateTextEdit.setObjectName("refreshRateTextEdit")
        self.horizontalLayout_3.addWidget(self.refreshRateTextEdit)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.powerLabel = QtWidgets.QLabel(self.centralwidget)
        self.powerLabel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.powerLabel.setObjectName("powerLabel")
        self.horizontalLayout_4.addWidget(self.powerLabel)
        self.powerTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.powerTextEdit.setMinimumSize(QtCore.QSize(0, 23))
        self.powerTextEdit.setMaximumSize(QtCore.QSize(16777215, 23))
        self.powerTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.powerTextEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.powerTextEdit.setReadOnly(True)
        self.powerTextEdit.setObjectName("powerTextEdit")
        self.powerTextEdit.viewport().setCursor(Qt.ArrowCursor)
        self.powerTextEdit.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout_4.addWidget(self.powerTextEdit)
        self.powerUnitsComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.powerUnitsComboBox.setMaximumSize(QtCore.QSize(16777215, 23))
        self.powerUnitsComboBox.setObjectName("powerUnitsComboBox")
        self.powerUnitsComboBox.addItem("")
        self.powerUnitsComboBox.addItem("")
        self.powerUnitsComboBox.setEnabled(False)
        self.horizontalLayout_4.addWidget(self.powerUnitsComboBox)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setObjectName("connectButton")
        self.connectButton.setEnabled(True)
        self.horizontalLayout_2.addWidget(self.connectButton)
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout_2.addWidget(self.refreshButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.showGraphPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.showGraphPushButton.setObjectName("showGraphPushButton")
        self.gridLayout.addWidget(self.showGraphPushButton, 1, 2, 1, 1)
        self.deviceComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.deviceComboBox.setObjectName("deviceComboBox")
        self.gridLayout.addWidget(self.deviceComboBox, 0, 1, 1, 1)
        self.disconnectButton = QtWidgets.QPushButton(self.centralwidget)
        self.disconnectButton.setObjectName("disconnectButton")
        self.disconnectButton.setEnabled(True)
        self.gridLayout.addWidget(self.disconnectButton, 0, 2, 1, 1)
        self.startAvgPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.startAvgPushButton.setObjectName("startAvgPushButton")
        self.gridLayout.addWidget(self.startAvgPushButton, 2, 0, 1, 1)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.avgPowerLabel = QtWidgets.QLabel(self.centralwidget)
        self.avgPowerLabel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerLabel.setObjectName("avgPowerLabel")
        self.horizontalLayout_6.addWidget(self.avgPowerLabel)
        self.avgPowerTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.avgPowerTextEdit.setMinimumSize(QtCore.QSize(0, 23))
        self.avgPowerTextEdit.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.avgPowerTextEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.avgPowerTextEdit.setReadOnly(True)
        self.avgPowerTextEdit.setObjectName("avgPowerTextEdit")
        self.avgPowerTextEdit.viewport().setCursor(Qt.ArrowCursor)
        self.avgPowerTextEdit.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout_6.addWidget(self.avgPowerTextEdit)
        self.avgPowerUnitsComboBox = QtWidgets.QComboBox(self.centralwidget)
        self.avgPowerUnitsComboBox.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerUnitsComboBox.setObjectName("avgPowerUnitsComboBox")
        self.avgPowerUnitsComboBox.addItem("")
        self.avgPowerUnitsComboBox.addItem("")
        self.horizontalLayout_6.addWidget(self.avgPowerUnitsComboBox)
        self.gridLayout.addLayout(self.horizontalLayout_6, 2, 1, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.avgPowerNLabel = QtWidgets.QLabel(self.centralwidget)
        self.avgPowerNLabel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerNLabel.setObjectName("avgPowerNLabel")
        self.horizontalLayout_7.addWidget(self.avgPowerNLabel)
        self.avgPowerNTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.avgPowerNTextEdit.setMinimumSize(QtCore.QSize(0, 23))
        self.avgPowerNTextEdit.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerNTextEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.avgPowerNTextEdit.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.avgPowerNTextEdit.setReadOnly(True)
        self.avgPowerNTextEdit.setObjectName("avgPowerNTextEdit")
        self.avgPowerNTextEdit.viewport().setCursor(Qt.ArrowCursor)
        self.avgPowerNTextEdit.setFocusPolicy(Qt.NoFocus)
        self.horizontalLayout_7.addWidget(self.avgPowerNTextEdit)
        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 490, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pm = Powermeter()

        self.connectButton.clicked.connect(self.connect_button_clicked)
        self.disconnectButton.clicked.connect(self.disconnect_button_clicked)
        self.refreshButton.clicked.connect(self.refresh_button_clicked)
        self.showGraphPushButton.clicked.connect(self.show_graph_button_clicked)
        self.powerUnitsComboBox.currentIndexChanged.connect(self.change_power_units)

        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")

        self.plotwindow = None

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Lumed TPM"))
        self.refreshRateLabel.setText(_translate("MainWindow", "Refresh Rate (s)"))
        self.powerLabel.setText(_translate("MainWindow", "Power"))
        self.powerUnitsComboBox.setItemText(0, _translate("MainWindow", "W"))
        self.powerUnitsComboBox.setItemText(1, _translate("MainWindow", "dBm"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.refreshButton.setText(_translate("MainWindow", "Refresh"))
        self.showGraphPushButton.setText(_translate("MainWindow", "Show/Hide Graph"))
        self.disconnectButton.setText(_translate("MainWindow", "Disconnect"))
        self.startAvgPushButton.setText(
            _translate("MainWindow", "Start/Stop Averaging")
        )
        self.avgPowerLabel.setText(_translate("MainWindow", "Average Power"))
        self.avgPowerUnitsComboBox.setItemText(0, _translate("MainWindow", "W"))
        self.avgPowerUnitsComboBox.setItemText(1, _translate("MainWindow", "dBm"))
        self.avgPowerNLabel.setText(_translate("MainWindow", "N"))

    def connect_button_clicked(self):
        self.connect_worker = Worker(
            self.pm.connect_device, self.deviceComboBox.currentText()
        )

        self.connect_worker.signals.result.connect(
            lambda result: (
                self.on_connect_disconnect() if result[0] == True else print(result[1])
            )
        )  # if successfully connected, run function, else print message
        self.connect_worker.signals.finished.connect(
            lambda: self.enable_disable_button(self.connectButton)
        )
        self.connect_worker.signals.error.connect(
            lambda e: (print(e), self.enable_disable_button(self.connectButton))[-1]
        )  # print error message and enable button
        self.connectButton.setEnabled(False)
        self.threadpool.start(self.connect_worker)

    def on_connect_disconnect(self):
        if self.pm.connected:
            # if successfully connected: measure power & enable/disable buttons
            self.enable_disable_button(self.refreshButton)
            self.enable_disable_button(self.powerUnitsComboBox)
            self.measure_power()
        else:
            # if successfully disconected device, enable refresh button
            self.enable_disable_button(self.refreshButton)
            self.enable_disable_button(self.powerUnitsComboBox)

    def disconnect_button_clicked(self):
        self.disconnect_worker = Worker(self.pm.disconnect_device)

        self.disconnect_worker.signals.result.connect(
            lambda result: (
                self.on_connect_disconnect() if result[0] == True else print(result[1])
            )
        )  # if successfully disconected device, print message & enable/disable buttons
        self.disconnect_worker.signals.finished.connect(
            lambda: self.enable_disable_button(self.disconnectButton)
        )
        self.disconnect_worker.signals.error.connect(
            lambda e: (print(e), self.enable_disable_button(self.disconnectButton))[-1]
        )  # print error message and enable button
        self.disconnectButton.setEnabled(False)
        self.threadpool.start(self.disconnect_worker)

    def refresh_button_clicked(self):
        self.refresh_worker = Worker(self.pm.list_devices)

        self.refresh_worker.signals.result.connect(
            lambda result: self.update_devices_combobox(result)
        )
        self.refresh_worker.signals.finished.connect(
            lambda: self.enable_disable_button(self.refreshButton)
        )
        self.refresh_worker.signals.error.connect(
            lambda e: (print(e), self.enable_disable_button(self.refreshButton))[-1]
        )  # print error message and enable button
        self.refreshButton.setEnabled(False)
        self.threadpool.start(self.refresh_worker)

    def enable_disable_button(self, button: QPushButton):
        button.setEnabled(not button.isEnabled())

    def measure_power(self):
        self.measure_power_worker = MeasurePowerWorker(self.pm)

        self.measure_power_worker.signals.progress.connect(
            lambda power, units: self.on_power_measurement(power, units)
        )
        self.measure_power_worker.signals.finished.connect(
            lambda: self.powerTextEdit.setPlainText("")
        )
        self.measure_power_worker.signals.error.connect(
            lambda e: (print(e), self.powerTextEdit.setPlainText(""))[-1]
        )  # print error message and clear power text edit
        self.threadpool.start(self.measure_power_worker)

    def on_power_measurement(self, power, units):
        # update power combobox & plot data
        self.powerTextEdit.setPlainText(f"{power} {units}")
        if self.plotwindow is not None:
            self.plotwindow.plotdata.append(power)
            self.plotwindow.plotwidget.plot(self.plotwindow.plotdata)

    def change_power_units(self):
        # update combobox & plot if created
        self.pm.power_units = self.powerUnitsComboBox.currentText()
        if self.plotwindow.isVisible():
            self.plotwindow = PlotWindow()
            self.plotwindow.plotwidget.getPlotItem().setLabel(
                "left", f"Power {self.pm.power_units}"
            )
            self.plotwindow.plotwidget.getPlotItem().setLabel("bottom", "X Axis")
            self.plotwindow.show()

    def update_devices_combobox(self, result: dict):
        self.deviceComboBox.clear()
        self.deviceComboBox.addItems(list(result.keys()))

    def show_graph_button_clicked(self):
        if self.plotwindow is None or self.plotwindow.isVisible() is False:
            # create plot if it doesn't exist or window was closed
            self.plotwindow = PlotWindow()
            self.plotwindow.plotwidget.getPlotItem().setLabel(
                "left", f"Power {self.pm.power_units}"
            )
            self.plotwindow.plotwidget.getPlotItem().setLabel("bottom", "X Axis")
            self.plotwindow.show()
            print("one")
        elif self.plotwindow.isVisible():
            # hide plot and wipe out its data
            self.plotwindow.hide()
            self.plotwindow = None
            print("two")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
