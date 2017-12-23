#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from a single mouse '''

from USB_Device import USB_Mouse

# Initialize a USB_Mouse object
device = USB_Mouse()

# Print default info (no attached device)
print "Device info:", device.get_info()

# Attach a device
device.attach()

# Print device info
print "Device info:", device.get_info()

# Read the device until keyboard interrupt (CTRL+C)
device.read()

# Check attached device list
print "Connected devices:", device.get_devices()

# Release the device
device.release()

# Check attached device list again
print "Connected devices:", device.get_devices()

# Print default info (no attached device)
print "Device info:", device.get_info()
