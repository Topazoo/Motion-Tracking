#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from multiple mice concurrently '''

from USB_Device import USB_Mouse

# Initialize USB_Mouse objects
device_1 = USB_Mouse()
device_2 = USB_Mouse()

# Pair with the first device
device_1.connect()

# Pair with the second device
device_2.connect()

# Read all connected devices concurrently with devices labeled
device_1.read_all(label=1)

# Disconnect devices
device_1.disconnect()
device_2.disconnect()
