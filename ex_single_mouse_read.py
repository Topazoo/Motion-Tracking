#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from a single mouse '''

from USB_Device import USB_Mouse

# Initialize a USB_Mouse object
device = USB_Mouse()

# Connect a device
device.connect()

# Read the device until keyboard interrupt (CTRL+C)
device.read()

# Disconnect the device
device.disconnect()
