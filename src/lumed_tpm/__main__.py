from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QPushButton
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
    """
    Custom Worker class used for continuous asynchronous power readings.

    Power values are emitted through the signal progress.

    """

    def __init__(self, pm: Powermeter):
        super().__init__()
        self.signals = WorkerSignals()
        self.pm = pm

    @pyqtSlot()
    def run(self):
        try:
            while self.pm.measuring:
                power, power_units = self.pm.power
                power = float("{:.2e}".format(power))
                self.signals.progress.emit(power, power_units)

                QThread.msleep(50)  # Refresh rate (ms)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.finished.emit()


class Worker(QRunnable):
    """
    Generic Worker class used for executing various functions.

    The running worker will execute a given function and emit data through its signals.

    """

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


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        try:
            self.ui.pm.disconnect_device()
        except Exception as e:
            print(e)


class Ui_MainWindow(object):

    ### INITIALIZE UI ###

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(740, 150)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.measureOncePushButton = QtWidgets.QPushButton(self.centralwidget)
        self.measureOncePushButton.setObjectName("measureOncePushButton")
        self.horizontalLayout_3.addWidget(self.measureOncePushButton)
        self.measureContinuousPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.measureContinuousPushButton.setObjectName("measureContinuousPushButton")
        self.horizontalLayout_3.addWidget(self.measureContinuousPushButton)
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
        self.horizontalLayout_4.addWidget(self.powerUnitsComboBox)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setObjectName("connectButton")
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
        self.gridLayout.addWidget(self.disconnectButton, 0, 2, 1, 1)

        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.avgPowerCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.avgPowerCheckBox.sizePolicy().hasHeightForWidth()
        )
        self.avgPowerCheckBox.setSizePolicy(sizePolicy)
        self.avgPowerCheckBox.setObjectName("avgPowerCheckBox")
        self.horizontalLayout_8.addWidget(self.avgPowerCheckBox)
        self.gridLayout_3.addLayout(self.horizontalLayout_8, 0, 0, 1, 1)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.avgPowerRateLabel = QtWidgets.QLabel(self.centralwidget)
        self.avgPowerRateLabel.setMaximumSize(QtCore.QSize(16777215, 23))
        self.avgPowerRateLabel.setObjectName("avgPowerRateLabel")
        self.horizontalLayout_10.addWidget(self.avgPowerRateLabel)
        self.avgPowerRateLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.avgPowerRateLineEdit.setObjectName("avgPowerRateLineEdit")
        self.horizontalLayout_10.addWidget(self.avgPowerRateLineEdit)
        self.gridLayout_3.addLayout(self.horizontalLayout_10, 0, 1, 1, 1)
        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 0, 1, 1)
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

        # Initialize the device driver
        self.pm = Powermeter()

        # Update UI elements
        self.on_connect_disconnect()

        # Initialize plotwindow from plots.py for plotting data
        self.plotwindow = None

        # Connect signals to event slots of the GUI
        self.connectButton.clicked.connect(self.connect_button_clicked)
        self.disconnectButton.clicked.connect(self.disconnect_button_clicked)
        self.refreshButton.clicked.connect(self.refresh_button_clicked)
        self.showGraphPushButton.clicked.connect(self.show_graph_button_clicked)
        self.powerUnitsComboBox.currentIndexChanged.connect(self.change_power_units)
        self.measureOncePushButton.clicked.connect(self.measure_once_button_clicked)
        self.measureContinuousPushButton.clicked.connect(self.measure_button_clicked)
        self.avgPowerCheckBox.stateChanged.connect(self.avgpower_checkbox_clicked)
        self.avgPowerRateLineEdit.textChanged.connect(
            self.avgpowerrate_lineedit_changed
        )

        # Initialize threadpool for running workers asynchronously
        self.threadpool = QThreadPool()
        print(f"Multithreading with maximum {self.threadpool.maxThreadCount()} threads")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Lumed TPM"))
        self.measureOncePushButton.setText(_translate("MainWindow", "Measure x1"))
        self.measureContinuousPushButton.setText(_translate("MainWindow", "Measure"))
        self.powerLabel.setText(_translate("MainWindow", "Power"))
        self.powerUnitsComboBox.setItemText(0, _translate("MainWindow", "W"))
        self.powerUnitsComboBox.setItemText(1, _translate("MainWindow", "dBm"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.refreshButton.setText(_translate("MainWindow", "Refresh"))
        self.showGraphPushButton.setText(_translate("MainWindow", "Show/Hide Graph"))
        self.disconnectButton.setText(_translate("MainWindow", "Disconnect"))
        self.avgPowerCheckBox.setText(_translate("MainWindow", "Averaging"))
        self.avgPowerRateLabel.setText(_translate("MainWindow", "Rate"))

    ### CUSTOM FUNCTIONS ###

    def on_connect_disconnect(self):
        if self.pm.connected:
            # successfully connected device
            self.refreshButton.setEnabled(False)
            self.powerUnitsComboBox.setEnabled(True)
            self.powerLabel.setEnabled(True)
            self.showGraphPushButton.setEnabled(True)
            self.measureOncePushButton.setEnabled(True)
            self.measureContinuousPushButton.setEnabled(True)
            self.avgPowerCheckBox.setEnabled(True)
            self.avgPowerRateLabel.setEnabled(True)
            self.avgPowerRateLineEdit.setEnabled(True)
        else:
            # successfully disconnected device
            self.refreshButton.setEnabled(True)
            self.powerUnitsComboBox.setEnabled(False)
            self.powerLabel.setEnabled(False)
            self.showGraphPushButton.setEnabled(False)
            self.measureOncePushButton.setEnabled(False)
            self.measureContinuousPushButton.setEnabled(False)
            self.avgPowerCheckBox.setEnabled(False)
            self.avgPowerRateLabel.setEnabled(False)
            self.avgPowerRateLineEdit.setEnabled(False)
            self.powerTextEdit.setPlainText("")

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
        )  # print error message and clear power textEdit
        self.threadpool.start(self.measure_power_worker)

    def on_power_measurement(self, power, units):
        # update power combobox & plot data
        self.powerTextEdit.setPlainText(f"{power} {units}")
        if self.plotwindow is not None and self.plotwindow.isVisible():
            self.plotwindow.plotdata.append(power)
            if len(self.plotwindow.plotdata) > 1000:  # clear up memory
                del self.plotwindow.plotdata[0]  # delete first data point
            self.plotwindow.plotwidget.clear()
            self.plotwindow.plotwidget.plot(self.plotwindow.plotdata)

    def update_devices_combobox(self, result: dict):
        self.deviceComboBox.clear()
        self.deviceComboBox.addItems(list(result.keys()))

    def change_power_units(self):
        # update combobox & plot if created
        self.pm.power_units = self.powerUnitsComboBox.currentText()
        if self.plotwindow is not None and self.plotwindow.isVisible():
            self.plotwindow = PlotWindow()
            self.plotwindow.plotwidget.getPlotItem().setLabel(
                "left", f"Power {self.pm.power_units}"
            )
            self.plotwindow.plotwidget.getPlotItem().setLabel("bottom", "X Axis")
            self.plotwindow.plotdata = []
            self.plotwindow.show()

    def on_avgpowercheckbox_changed(self, state):
        if state == Qt.Checked:
            self.pm.averaging_rate = self.avgPowerRateLineEdit.text()
        elif state == Qt.Unchecked:
            self.pm.averaging_rate = 1

    def change_averaging_rate(self, rate):
        if self.avgPowerCheckBox.checkState() == Qt.Checked:
            self.pm.averaging_rate = rate

    ### EVENT SLOTS ###

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

    def show_graph_button_clicked(self):
        if self.plotwindow is None or self.plotwindow.isVisible() is False:
            # create plot if it doesn't exist or window was closed
            self.plotwindow = PlotWindow()
            self.plotwindow.plotwidget.getPlotItem().setLabel(
                "left", f"Power {self.pm.power_units}"
            )
            self.plotwindow.plotwidget.getPlotItem().setLabel("bottom", "X Axis")
            self.plotwindow.show()
        elif self.plotwindow.isVisible():
            # hide plot and wipe out its data
            self.plotwindow.hide()
            self.plotwindow = None

    def measure_once_button_clicked(self):
        def read_power_once():
            power, power_units = self.pm.power
            power = str(float("{:.2e}".format(power)))
            return power, power_units

        self.connect_worker = Worker(read_power_once)
        self.connect_worker.signals.result.connect(
            lambda result: self.on_power_measurement(result[0], result[1])
        )  # result: ('power value', 'power units')
        self.connect_worker.signals.error.connect(
            lambda e: print(e)
        )  # print error message
        self.threadpool.start(self.connect_worker)

    def measure_button_clicked(self):
        if self.pm.measuring == False:
            # start measuring & disable measure once button
            self.pm.measuring = True
            self.measureOncePushButton.setEnabled(False)
            self.measure_power()
        elif self.pm.measuring == True:
            # stop measuring & enable measure once button
            self.pm.measuring = False
            self.measureOncePushButton.setEnabled(True)

    def avgpower_checkbox_clicked(self):
        self.connect_worker = Worker(
            self.on_avgpowercheckbox_changed, self.avgPowerCheckBox.checkState()
        )
        self.connect_worker.signals.error.connect(lambda e: print(e))
        self.threadpool.start(self.connect_worker)

    def avgpowerrate_lineedit_changed(self):
        self.connect_worker = Worker(
            self.change_averaging_rate, self.avgPowerRateLineEdit.text()
        )
        self.connect_worker.signals.error.connect(lambda e: print(e))
        self.threadpool.start(self.connect_worker)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindowController()
    mainWin.show()
    sys.exit(app.exec_())
