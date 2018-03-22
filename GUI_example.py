#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Test the graphical interface layer for the optical mouse reader.

    Version: Python 2.7'''

from GUI_Layer import  *
from PyQt4.QtGui import *

def main():
    app = QApplication(sys.argv)
    mw = MainWindow()

    # Start the event loop...
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()