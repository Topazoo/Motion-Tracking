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
device_0.read_all(sync=False)

# Loop reading 50 movements from both devices
x = 0
while(x < 50):
    movement_0 = device_0.get_movement(label=True)
    movement_1 = device_1.get_movement(label=True)
    movement = (movement_0, movement_1)

    if(movement != (None, None)):
        print (movement_0, movement_1)
        x += 1

# Loop reading 50 movements from device 1
x = 0
while(x < 50):
    movement = device_1.get_movement(label=True)
    if(movement != None):
        print movement
        x += 1

# Disconnect devices
device_0.disconnect()
device_1.disconnect()
