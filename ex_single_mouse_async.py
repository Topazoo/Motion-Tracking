#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Read data from a single mouse asynchronously'''

from USB_Device import USB_Mouse

# Initialize a USB_Mouse object
device = USB_Mouse()

# Connect a device
device.connect()

# Read the device in the background
device.read(sync=False)

# Loop reading 20 movements
x = 0
while(x < 20):
    movement = device.get_movement()
    if(movement != None):
        print movement
        x += 1

# Disconnect the device
device.disconnect()
