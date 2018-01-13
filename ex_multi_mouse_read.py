#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from multiple mice concurrently '''

from USB_Device import USB_Mouse

# Initialize USB_Mouse objects
device_0 = USB_Mouse()
device_1 = USB_Mouse()

# Pair with the first device
device_0.connect()

# Pair with the second device
device_1.connect()

# Read all connected devices concurrently with devices labeled
device_0.read_all(label=True)

# Disconnect devices
device_0.disconnect()
device_1.disconnect()
