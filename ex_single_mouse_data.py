#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Display information about a single mouse '''

from USB_Device import USB_Mouse

# Initialize a USB_Mouse object
device = USB_Mouse()

# Print default info (no attached device)
print "Device info:", device.get_info()

# Connect a device
device.connect()

# Print device info
print "Device info:", device.get_info()

# Check attached device list
print "Connected devices:", device.get_devices()

# Disconnect the device
device.disconnect()

# Check attached device list again
print "Connected devices:", device.get_devices()
