#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from multiple mice concurrently '''

from USB_Device import USB_Mouse

# Initialize USB_Mouse objects
device_1 = USB_Mouse()
device_2 = USB_Mouse()

device_1.attach()

# Print device_1 info
print "Device info:", device_1.get_info()

device_2.attach()

# Print device_1 info
print "Device info:", device_2.get_info()

# Read connected devices concurrently
device_1.read_all(1)

#device_1.release()
#device_2.release()
