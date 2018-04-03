#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Graphical interface layer for the optical mouse reader.

    Note: Many thanks to https://nikolak.com/pyqt-threading-tutorial/ for the UTF-8 encoding functions and example
    code for PyQt threading.

    Version: Python 2.7 '''

import sys
from PyQt4 import QtCore, QtGui
from USB_Device import Mouse_Movement, USB_Mouse

class Ui_MainWindow(QtGui.QMainWindow):
    ''' Main window of the GUI '''

    def __init__(self):
        super(self.__class__, self).__init__()
        self.tracking = USB_Mouse()
        self.setup_UI(self)

    def setup_UI(self, MainWindow):
        ''' Set up main window interface '''

        # Name, size and icon
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(526, 373)
        self.setWindowIcon(QtGui.QIcon('icons/main.png'))

        self.add_menu()
        self.add_central_widget(MainWindow)
        self.add_data_display()

        MainWindow.setCentralWidget(self.centralwidget)

        # Connect slots to labels
        self.translate_UI(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.show()

    def add_menu(self):
        ''' Build the menubar '''

        self.statusBar()
        self.menubar = self.menuBar()

        self.fileMenuOptions(self.menubar)
        self.devMenuOptions(self.menubar)

    def add_central_widget(self, MainWindow):
        ''' Build the central widget '''

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))

    def add_data_display(self):
        ''' Add field to display data '''

        # Build widget to display data list label
        self.data_list_label = QtGui.QLabel(self.centralwidget)
        self.data_list_label.setObjectName(_fromUtf8("data_list_label"))
        self.verticalLayout.addWidget(self.data_list_label)

        # Build widget for data list
        self.data_list = QtGui.QListWidget(self.centralwidget)
        self.data_list.setBatchSize(1)
        self.data_list.setObjectName(_fromUtf8("data_list"))
        self.verticalLayout.addWidget(self.data_list)

        # Build widget for stop button
        self.stop_button = QtGui.QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_read)
        self.verticalLayout.addWidget(self.stop_button)

    def stop_read(self):
        ''' Stop reading a device '''

        QtGui.QMessageBox.question(self, 'Success', "Read stopped", QtGui.QMessageBox.Ok)
        self.stop_button.setEnabled(False)
        self.tracking.event.clear()

    def translate_UI(self, MainWindow):
        ''' Label to connect slots '''

        MainWindow.setWindowTitle(_translate("MainWindow", "Track Devices", None))
        self.data_list_label.setText(_translate("MainWindow", "Tracking Data:", None))

    def fileMenuOptions(self, menubar):
        ''' Add options to the file menu'''

        fileMenu = menubar.addMenu('&File')

        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtGui.qApp.quit)

        fileMenu.addAction(exitAction)

    def devMenuOptions(self, menubar):
        ''' Add options to the devices menu'''

        devicesMenu = menubar.addMenu('&Devices')

        # Add device menu option
        self.addDevice = QtGui.QAction(QtGui.QIcon('exit.png'), '&Add Device', self) # Change icon !
        self.addDevice.setShortcut('Ctrl+A')
        self.addDevice.setStatusTip('Add a device')

        # Triggering launches add_device wrapper
        self.addDevice.triggered.connect(self.addWrapper)

        # Remove device menu option
        self.remDevice = QtGui.QAction(QtGui.QIcon('exit.png'), '&Remove Device', self) # Change icon !
        self.remDevice.setShortcut('Ctrl+R')
        self.remDevice.setStatusTip('Remove a device')
        self.remDevice.setEnabled(False)

        # Triggering removes the device
        self.remDevice.triggered.connect(self.removeWrapper)

        devicesMenu.addAction(self.addDevice)
        devicesMenu.addAction(self.remDevice)

    def addWrapper(self):
        ''' Add and read a device '''

        # Prompt user then poll system
        QtGui.QMessageBox.question(self, 'Message', "Ensure the device is disconnected", QtGui.QMessageBox.Ok)
        guids = self.tracking.getDeviceIDs()
        QtGui.QMessageBox.question(self, 'Message', "Please connect the device", QtGui.QMessageBox.Ok)

        # Handle errors
        ret = self.tracking.connect(1, guids)
        if(self.errorHandler(ret) == -1):
            return

        QtGui.QMessageBox.question(self, 'Success', "Found device!", QtGui.QMessageBox.Ok)
        self.stop_button.setEnabled(True)
        self.remDevice.setEnabled(True)
        self.addDevice.setEnabled(False)

        # Begin threaded read of device
        self.get_thread = getDataThread(self.tracking)
        self.connect(self.get_thread, QtCore.SIGNAL("get_tracked_data(QString)"), self.update_Data)
        self.get_thread.start()

    def removeWrapper(self):
        ''' Remove a device '''

        if(self.tracking.event.isSet()):
            self.stop_read()

        self.tracking.disconnect()
        self.remDevice.setEnabled(False)
        self.addDevice.setEnabled(True)
        QtGui.QMessageBox.question(self, 'Success', "Device disconnected!", QtGui.QMessageBox.Ok)

    def update_Data(self, data):
        ''' Post data to GUI '''

        self.data_list.insertItem(0, data)

    def errorHandler(self, ret):
        ''' Handle device attachment errors on frontend '''

        if(ret == -1):
            QtGui.QMessageBox.question(self, 'Error', "Multiple devices detected!", QtGui.QMessageBox.Ok)
            return -1
        elif (ret == -2):
            QtGui.QMessageBox.question(self, 'Error', "No device detected!", QtGui.QMessageBox.Ok)
            return -1
        elif (ret == -3):
            QtGui.QMessageBox.question(self, 'Error', "Vendor/Product ID Mismatch!", QtGui.QMessageBox.Ok)
            return -1


class getDataThread(QtCore.QThread):
    ''' Read and display device data via modified PyQt thread'''

    def __init__(self, device):
        QtCore.QThread.__init__(self)
        self.device = device

    def __del__(self):
        self.wait()

    def run(self):
        ''' Read the device and update the GUI '''

        self.device.read(gui=1)
        while(1):
            try:
                if(self.device.movements.empty() is False):
                    data = self.device.get_movement(False, 2)
                    if(data is not None):
                        self.emit(QtCore.SIGNAL('get_tracked_data(QString)'), str(data))
            except:
                continue

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

def main():
    app = QtGui.QApplication(sys.argv)
    mw = Ui_MainWindow()

    # Start the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()