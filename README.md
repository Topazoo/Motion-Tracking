# Class to Read Optical Mouse Movements

## Overview:
The USB_Device class allows the the user to read data from a
physically attached USB device. 

## Requirements:
###	Python 2.7
https://www.python.org/download/releases/2.7/

###	pyusb
https://github.com/pyusb/pyusb

## Functionality:
### 	Creation: 
```
	device = USB_Device()
```
Creates an object ready to pair with a physical device

###	Attaching a Device
```
	device.attach()
```
Prompts the user to attach the device and verifies the
script has taken control of the device from the kernel

###	Reading Data:
```
	device.read()
```
Reads mouse movements

###	Releasing the Device
```
	device.release()
```
Gives control of the device back to the kernel
			  
###	Example:
``` 
sudo python 
>>> from mouse_track import USB_Device
>>> device = USB_Device()
>>> device.attach()
Ensure the USB device you want to track is detached and press Enter >>>
Please reattach the USB device and press Enter >>>
Device 2361 attached!
>>> device.read()
[0, 255, 0, 0]
[0, 255, 1, 0]
[0, 1, 0, 0]
[0, 1, 255, 0]
...
```

## Interpreting Data
### Information for interpreting gathered data can be found at:
https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack

