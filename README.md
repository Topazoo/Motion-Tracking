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

###	Reading Data:
```
	device.read()
```
	Prompts the user to attach the device, pairs, and reads mouse 
	movement data.
			  
###	Example:
``` 
sudo python 
>>> from mouse_track import USB_Device
>>> device = USB_Device()
>>> device.read()
Ensure the USB device you want to track is detached and press Enter >>>
Please reattach the USB device and press Enter >>>
[0, 255, 0, 0]
[0, 255, 1, 0]
[0, 1, 0, 0]
[0, 1, 255, 0]
...
```

## Interpreting Data
### Information for interpreting gathered data can be found at:
https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack

