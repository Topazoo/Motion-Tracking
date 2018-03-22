#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Graphical interface layer for the optical mouse reader.

    Version: Python 2.7'''


import sys
from USB_Device import Mouse_Movement, USB_Mouse
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.tracking = USB_Mouse()
        self.mdi = QtGui.QMdiArea()
        self.setCentralWidget(self.mdi)
        self.mdi.tileSubWindows()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 500, 500)
        self.setWindowTitle('Tracking Data')
        self.setWindowIcon(QtGui.QIcon('icons/main.png'))
        self.show()
        self.addMenu()

    def addMenu(self):
        self.statusBar()
        menubar = self.menuBar()

        fileMenuOptions(self, menubar)
        devMenuOptions(self, menubar)

    def errorHandler(self, ret):
        if(ret == -1):
            QtGui.QMessageBox.question(self, 'Error', "Multiple devices detected!", QtGui.QMessageBox.Ok)
            return -1
        elif (ret == -2):
            QtGui.QMessageBox.question(self, 'Error', "No device detected!", QtGui.QMessageBox.Ok)
            return -1
        elif (ret == -3):
            QtGui.QMessageBox.question(self, 'Error', "Vendor/Product ID Mismatch!", QtGui.QMessageBox.Ok)
            return -1

    def addWrapper(self):
        QtGui.QMessageBox.question(self, 'Message', "Ensure the device is disconnected", QtGui.QMessageBox.Ok)
        guids = self.tracking.getDeviceIDs()
        QtGui.QMessageBox.question(self, 'Message', "Please connect the device", QtGui.QMessageBox.Ok)

        ret = self.tracking.connect(1, guids)

        if(self.errorHandler(ret) == -1):
            return

        device = self.tracking.con_devices[self.tracking.index]

        QtGui.QMessageBox.question(self, 'Success', "Found device!", QtGui.QMessageBox.Ok)

        dt = MouseData(device.prod_id, self.tracking.index)
        self.mdi.addSubWindow(dt)
        self.show()
        dt.show()


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

class MouseData(QtGui.QMdiSubWindow):
    ''' Sub window for individual mouse data '''

    def __init__(self, prod_id, index):
        super(MouseData, self).__init__()
        self.initUI(prod_id, index)

    def initUI(self, prod_id, index):
        self.setWindowTitle("Device " + str(index + 1) +": " + str(prod_id))
        self.setWidget(QtGui.QTextEdit())
        self.show()

def fileMenuOptions(main_window, menubar):
    ''' Add options to the file menu'''

    fileMenu = menubar.addMenu('&File')

    exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', main_window)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(QtGui.qApp.quit)

    fileMenu.addAction(exitAction)

def devMenuOptions(main_window, menubar):
    ''' Add options to the devices menu'''

    devicesMenu = menubar.addMenu('&Devices')

    addDevice = QtGui.QAction(QtGui.QIcon('exit.png'), '&Add Device', main_window)
    addDevice.setShortcut('Ctrl+A')
    addDevice.setStatusTip('Add a device')

    # Triggering launches add_device wrapper
    addDevice.triggered.connect(main_window.addWrapper)  # Change!

    # remDevice = QtGui.QAction(QtGui.QIcon('exit.png'), '&Remove Device', main_window)
    # remDevice.setShortcut('Ctrl+R')
    # remDevice.setStatusTip('Remove a device')
    # remDevice.triggered.connect(QtGui.qApp.quit) #Change!

    devicesMenu.addAction(addDevice)
    # devicesMenu.addAction(remDevice)
#    def normalOutputWritten(self, text):
#        """Append text to the QTextEdit."""
#        # Maybe QTextEdit.append() works as well, but this is how I do it:
#       cursor = self.te.textCursor()
#        cursor.movePosition(QtGui.QTextCursor.End)
#        cursor.insertText(text)
#       self.te.setTextCursor(cursor)
#        self.te.ensureCursorVisible()
