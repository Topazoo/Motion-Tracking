# Class to Read Optical Mouse Movements

## Overview:
The USB_Mouse class allows the the user to read data from a
physically attached USB mouse. 

## Requirements:
###	Python 2.7:
https://www.python.org/download/releases/2.7/

###	pyusb:
https://github.com/pyusb/pyusb

###	Superuser Privileges

## Methods:
### 	Creation: 
```
	device = USB_Mouse()
```
Creates an object ready to pair with a physical mouse

###	Attaching a Device:
```
	device.attach()
```
Prompts the user to attach the mouse and verifies the
script has taken control of the device from the kernel.
Returns 0 for successful attachment and -1 for failure.

###	Reading Data From a Single Device:
```
	device.read()

	device.read(label=1)
```
Reads mouse movements until a keyboard interrupt (CTRL+C)
is detected.
Returns 0 for a successful read and -1 for failure.

Parameters: 
* label: labels the data with the device it was read from.
	* 0 - Default. Data is unlabeled.
	* 1 - Data is labeled.

### Reading Data From Multiple Devices:
```
	device.read_multiple([devices]) 
					
	device.read_multiple([devices], label=1)
```
Reads concurrent mouse movements from a list of devices.
Returns 0 for a successful read and -1 for failure.

Parameters: 
* [devices]: A list of USB_Mouse objects connected to physical devices.
* label: Labels the data with the device it was read from.
	* 0 - Default. Data is unlabeled.
	* 1 - Data is labeled.

```
	device.read_all()
	
	device.read_all(label=1)
```
Reads concurrent mouse movement from all USB_Mouse objects that
are connected to a physical device. This method may be invoked 
through any USB_Mouse object (even if it is not connected to a
physical device).
Returns 0 for a successful read and -1 for failure.

Parameters: 
* label: labels the data with the device it was read from.
	* 0 - Default. Data is unlabeled.
	* 1 - Data is labeled.

###	Releasing the Device:
```
	device.release()
```
Gives control of the device back to the kernel. 
Returns 0 for successful release and -1 for failure.

### Getting Device Information:
```
	device.get_info()
```
Returns a tuple containing the device number, index of the device
in the shared connected devices list, device product ID,
device vendor ID, and the number of connected devices. The default
value is -1 for all variables but the last which has a default of 0.
Values are default if no device is attached.

### Getting Connected Devices:
```
	device.get_devices()
```
Returns a list of all USB_Mouse objects currently paired to a physical
device. This list can be accessed from any USB_Mouse object (even
if it isn't paired with a device).
			  
##	Simple Example:
``` 
sudo python 
>>> from USB_Mouse()
>>> device.attach()
Ensure the USB device you want to track is detached and press Enter >>>
Please reattach the USB device and press Enter >>>
Device 0 attached!
>>> device.read()
[0, 255, 0, 0]
[0, 255, 1, 0]
[0, 1, 0, 0]
[0, 1, 255, 0]
...
>>> device.release()
Device 0 released!
```

## More Examples Can Be Found In:
single_mouse_example.py
multi_mouse_example.py

## Known Issues:
### Errno 16/19 on Attachment:
Usually this occurs if the Enter key is pressed too quickly after a
mouse is attached. Ensure the mouse has been given enough time to 
be fully detected by the operating system.

### Concurrency Keyboard Interrupts:
Currently there is no way to interrupt concurrent threads with a keyboard interrupt.
Concurrent reads require a forced exit. This will be fixed in the very near future.

## Interpreting Data:
### Information for interpreting gathered data can be found at:
https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack
