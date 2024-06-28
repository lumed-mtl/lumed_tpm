from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QRunnable, QObject, QThread, pyqtSlot, QThreadPool, pyqtSignal

from powermeter import Powermeter


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `str` Exception string

    result
        `tuple` data returned from processing

    update
        `object` data for inter-thread communication

    """

    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(tuple)
    update = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, func=None, *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.is_killed = False

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

    def kill(self):
        self.is_killed = True


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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
