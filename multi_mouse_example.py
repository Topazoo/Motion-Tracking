#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from multiple mice concurrently '''

from USB_Device import USB_Mouse

# Initialize USB_Mouse objects
device_1 = USB_Mouse()
device_2 = USB_Mouse()

# Pair with the first device
device_1.attach()

# Print device_1 info
print "Device info:", device_1.get_info()

# Pair with the second device
device_2.attach()

# Print device_2 info
print "Device info:", device_2.get_info()

# Read all connected devices concurrently with devices labeled
device_1.read_all(1)

# Read a list of devices concurrently with devices labeled
device_2.read_multiple([device_1, device_2], 1)

# Release devices
device_1.release()
device_2.release()
