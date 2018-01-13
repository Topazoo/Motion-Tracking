# Class to Read Concurrent Optical Mouse Movements

## Overview:
The USB_Mouse class allows the the user to read data from a
physically attached USB mouse.

## Requirements:
###	Python 2.7:
https://www.python.org/download/releases/2.7/

###	pyusb:
pip install pyusb

###	Superuser Privileges
sudo

## Methods:
### Creation:
```
	device = USB_Mouse()
```
Creates an object ready to pair with a physical mouse.

###	Connecting to a Device:
```
	device.connect()
```
Prompts the user to connect the mouse and verifies the
script has taken control of the device from the kernel.
Returns -1 on failure.

###	Reading Data From One or More Devices:
```
	device.read()

	device.read(devices=None)

	device.read(sync=True)

	device.read(label=False)

	device.read(verbosity=2)
```
Reads movement data from one or mice until a keyboard interrupt (CTRL+C)
or program exit is detected.
Returns -1 on failure.

Parameters:
* [devices]: A list of USB_Mouse objects connected to physical devices to read.
* sync: Prints data continuously or runs read() in the background
	* True - Default. Data is read and printed until interrupted with CTRL-C.
	* False - Data is read in the background.
* label: labels the data with the device it was read from.
	* False - Default. Data is unlabeled.
	* True - Data is labeled.
* verbosity: how the data is represented.
	* 0 - None.
	* 1 - Raw. Eight element list of movements.
	* 2 - Default. Two element list of (direction, speed) tuples.

### All Devices:
```
	device.read_all()

	device.read_all(sync=True)

	device.read_all(label=True)

	device.read_all(verbosity=2)
```
Reads concurrent mouse movement data from all USB_Mouse objects that
are connected to a physical device until a keyboard interrupt (CTRL+C)
or program exit is detected. This method may be invoked from any USB_Mouse object (even if it is not connected to a physical device).
Returns -1 on failure.

Parameters:
* label: labels the data with the device it was read from.
	* False - Data is unlabeled.
	* True - Default. Data is labeled.
* sync: Prints data continuously or runs read() in the background
	* True - Default. Data is read and printed until interrupted with CTRL-C.
	* False - Data is read in the background.
* verbosity: how the data is represented.
	* 0 - None.
	* 1 - Raw. Eight element list of movements.
	* 2 - Default. Two element list of (direction, speed) tuples.

###	Releasing a Device:
```
	device.disconnect()
```
Gives control of the device back to the kernel.
Returns -1 on failure.

### Getting Device Information:
```
	device.get_info()
```
Returns a tuple containing the device number, index of the device
in the shared connected devices list, device product ID,
device vendor ID, and the number of connected devices. The default
value is -1 for all variables but the last which has a default of 0.
Values are default if no device is attached.

```
	device.get_movement()

	device.get_movement(label=False)

	device.get_movement(verbosity=2)
```
Gets the the latest mouse movement data for the device. Generally
used to access movement being read by a read(sync=False) call
in the background when necessary.
Returns None if a new movement hasn't been read yet
Returns a list based on the verbosity parameter otherwise
* label: labels the data with the device it was read from.
	* False - Data is unlabeled.
	* True - Default. Data is labeled.
* verbosity: how the data is represented.
	* 0 - None.
	* 1 - Raw. Eight element list of movements.
	* 2 - Default. Two element list of (direction, speed) tuples.

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
>>> from USB_Device import USB_Mouse
>>> device = USB_Mouse()
>>> device.connect()
Please disconnect the USB device and press Enter >>>
Please connect the USB device and press Enter >>>
Device 0 connected
>>> device.read()
[('Left', 11), ('Down', 3)]
[('Left', 22), ('Down', 3)]
[('Left', 32), ('Down', 3)]
[('Left', 37), ('Down', 6)]
[('Left', 42), ('Down', 5)]
[('Left', 42), ('Down', 7)]
[('Left', 32), ('Down', 5)]
[('Left', 27), ('Down', 4)]
[('Left', 18), ('Down', 3)]
...
>>> device.disconnect()
Device 0 disconnected
```

## More Examples Can Be Found In /examples:
* ex_single_mouse_data.py
	* Connect a single device and display information about it.
* ex_single_mouse_read.py
	* Connect a single device and read information from it.
* ex_single_mouse_async.py
	* Connect a single device and read information from it
	  asynchronously.
* ex_multi_mouse_read.py
	* Connect to multiple devices and read labeled information from them.
* ex_multi_mouse_async.py
	* Connect to multiple devices and read labeled information from them asynchronously.

## Known Issues:
### Errno 16/19 on Attachment:
Usually this occurs if the Enter key is pressed too quickly after a
mouse is attached. Ensure the mouse has been given enough time to
be fully detected by the operating system.

### Errno 16 on Detachment:
Happens after a multi-mouse asynchronous read for currently unknown reasons. No ill effects other than the kernel not regaining
control of the mouse on program exit.

### Incorrect Readings:
The script reads data from an AmazonBasics 3-Button Wired Mouse by default.
The default configuration works with other models of mice, but not all.
If it is giving you the wrong verbose readings, you need to configure the
parameters of __init()__ in the Mouse_Movement class.

	1. Read the data array of the attached device with USB_Mouse.read(verbosity=0)

	2. If your movement columns not the same as the default columns:
			lr_col = the column in the data array that changes with left and right movement
			ud_col = the column in the data array that changes with up and down movement

	3. If the range of movement values in both columns is not 0 - 255:
			lr_max = the maximum movement value for left and right movement
			ud_max = the maximum movement value for up and down movement

	4. If right movement values are larger than left movement values
			rev_lr = 1

	5. If down movement values are larger than up movement values
			rev_ud = 1

## Upcoming Features:
### Auto detect mouse configurations
I should be able to add a feature to allow the mouse config to be set by a few test readings. It's a hassle setting new configs right now.