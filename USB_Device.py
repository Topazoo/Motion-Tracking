#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Class to track optical mouse motion via USB. Can
    track data from multiple mice concurrently.

    Version: Python 2.7

    Methods inspired by:
    https://www.orangecoat.com/how-to/use-pyusb-to-find-vendor-and-product-ids-for-usb-devices
    https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack
    https://stackoverflow.com/questions/21731043/use-of-input-raw-input-in-python-2-and-3 '''

from collections import Counter
from threading import Thread, Event
import usb.core
import usb.util
import Queue

class Mouse_Movement(object):
    ''' Analyze the movement of USB Mouse, the default is below
        https://www.amazon.com/AmazonBasics-3-Button-Wired-Mouse-Black/dp/B005EJH6RW

        To configure with a different mouse:

        1. Read the data array of the attached device with USB_Mouse.read(verbosity=0)
        2. If your values are not the default values, set them accordingly:
                lr_col = the column in the data array that changes with left and right movement
                ud_col = the column in the data array that changes with up and down movement
        3. If the range of movement values is not 0 - 255, set these accordingly:
                lr_max = the maximum movement value in the data array for left and right movement
                ud_max = the maximum movement value in the data array for up and down movement
        4. If right movement values are larger than left movement values
                rev_lr = 1
        5. If downward movement values are larger than upward movement values
                rev_ud = 1 '''

    def __init__(self, device, data_list, lr_col=1, ud_col=2,
                 lr_max=255, ud_max=255, rev_lr=0, rev_ud=0):

        self.lr_col = lr_col        # Left/Right col in data array
        self.ud_col = ud_col        # Up/Down col in data array
        self.lr_max = lr_max + 1    # Left/Right maximum value
        self.ud_max = ud_max + 1    # Up/Down maximum value
        self.rev_lr = rev_lr        # Reverse Left/Right (Right max)
        self.rev_ud = rev_ud        # Reverse Up/Down (Down max)

        self.raw = data_list        # Raw data

        self.left_right = "None"    # Movement direction
        self.up_down = "None"
        self.left_right_spd = 0     # Movement speed
        self.up_down_spd = 0
        self.left_right_acc = 0     # Movement acceleration
        self.up_down_acc = 0
        self.device = device        # Device

        self.analyze_dir()          # Analyze raw data
        self.analyze_spd()

    def analyze_dir(self):
        ''' Use the raw data collected from the mouse to
            determine its direction '''

        # Calculate the median of possible l/r and u/d
        # values. Movements share one column in the data, so
        # direction is represented by a value on either side
        # of the median

        lr_median = self.lr_max/2
        ud_median = self.ud_max/2

        # If there is movement in the l/r column in the raw data
        if(self.raw[self.lr_col] > 0):
            # Values below the median are right movement
            if(self.raw[self.lr_col] < lr_median):
                self.left_right = "Right"
            # Values above the median are left movement
            elif(self.raw[self.lr_col] > lr_median):
                self.left_right = "Left"

        if(self.raw[self.ud_col] > 0):
            if(self.raw[self.ud_col] < ud_median):
                self.up_down = "Down"
            elif(self.raw[self.ud_col] > ud_median):
                self.up_down = "Up"

        # Reverse movement if flag is set
        if(self.rev_lr == 1 and self.left_right is "Right"):
            self.left_right = "Left"
        elif(self.rev_lr == 1 and self.left_right is "Left"):
            self.left_right = "Right"

        if(self.rev_ud == 1 and self.up_down is "Up"):
            self.up_down = "Down"
        elif(self.rev_ud == 1 and self.up_down is "Down"):
            self.up_down = "Up"


    def analyze_spd(self):
        ''' Determine the speed of movement and represent as a range
            with 0 being no movement, and 100 being maximum recordable
            speed '''

        lr_median = self.lr_max/2
        ud_median = self.ud_max/2

        # If movement is detected in the l/r column of the raw data
        if(self.raw[self.lr_col] > 0):
            # Values below the median are right movement
            if(self.raw[self.lr_col] < lr_median):
                # Calculate direction, then rate of speed based on range of possible values
                self.left_right_spd = int(self.raw[self.lr_col]/float(lr_median - 1) * 100)
            elif(self.raw[self.lr_col] > lr_median):
                self.left_right_spd = int(((self.lr_max - self.raw[self.lr_col])/float(lr_median - 1)) * 100)

        if(self.raw[self.ud_col] > 0):
            if(self.raw[self.ud_col] < ud_median):
                self.up_down_spd = int(self.raw[self.ud_col]/float(ud_median - 1) * 100)
            elif(self.raw[self.ud_col] > ud_median):
                self.up_down_spd = int(((self.ud_max - self.raw[self.ud_col])/float(ud_median - 1)) * 100)

    def get_raw(self, label=False):
        ''' Return raw data '''

        if(label is False):
            return self.raw
        else:
            return "Device: " + str(self.raw)

    def get_dir(self, label=False):
        ''' Return movement direction. The label flag will
            label data by device. '''

        if(label is False):
            return (self.left_right, self.up_down)
        else:
            return("Device: " + str(self.device), self.left_right,
                   self.up_down)

    def get_spd(self, label=False):
        ''' Return movement direction '''

        if(label is False):
            return(self.left_right_spd, self.up_down_spd)
        else:
            return("Device: " + str(self.device),
                   self.left_right_spd,
                   self.up_down_spd)

    def get_data(self, label=False):
        ''' Return movement data '''

        data = []

        direc = self.get_dir()                  # Direction
        speed = self.get_spd()                  # Speed
        data.append((direc[0], speed[0]))
        data.append((direc[1], speed[1]))

        if(label is False):
            return data
        else:
            return("Device: " + str(self.device), data)

class USB_Mouse(object):
    ''' Read USB Mouse tracking data '''

    # Class Variables - (Shared by all instances)
    num_con_devices = 0
    con_devices = []

    def __init__(self):
        self.prod_id = -1   # Device product ID
        self.vendor = -1    # Device vendor ID
        self.device = -1    # A usb.core device object placeholder
        self.endpoint = -1  # A usb.core device attribute placeholder
        self.num = -1       # Class ID for classes with connected devices
        self.index = -1     # Index in connected devices list
        self.interface = 0  # Device constant

        self.movements = Queue.Queue()  # Recorded movements
        self.event = Event()            # Shared variable to synchronize threads

    def connect(self, gui=0, guids=[[], []]):
        ''' Take control of the device and read data '''

        # Find the device to attach to
        ids = self.find_device(gui, guids)

        if(ids < 0):
            if(gui == 0):
                print("Failed to connect to a device...")
            return ids

        self.vendor = ids[0][0]
        self.prod_id = ids[1][0]
        self.device = usb.core.find(idVendor=self.vendor, idProduct=self.prod_id)

        # Take control from the kernel
        self.claim_device()

        # Check success
        if (self.prod_id == -1 or self.device == -1 or self.vendor == -1):
            if(gui == 0):
                print("No device attached!")
            return -2

        # Update shared number of connected devices
        self.num = USB_Mouse.num_con_devices
        USB_Mouse.num_con_devices += 1

        # Store device so all connected devices can be accessed with one object
        USB_Mouse.con_devices.append(self)
        self.index = len(self.con_devices) - 1

        if(gui == 0):
            print("Device " + str(self.num) + " connected")

    def getDeviceIDs(self):
        ''' Get all connected devices '''

        dev_ids = [[], []]
        devices = usb.core.find(find_all=True)

        # Store a list of all attached vendor and product IDs
        for cfg in devices:
            dev_ids[0].append(int(cfg.idVendor))
            dev_ids[1].append(int(cfg.idProduct))

        return dev_ids

    def find_device(self, gui=0, guids=[[], []]):
        ''' Find a USB device '''

        final = []

        if(gui == 0): # Already ran in GUI wrapper
            raw_input("Ensure the device is disconnected and press Enter >>> ")
            guids = self.getDeviceIDs()
            raw_input("Please connect the USB device and press Enter >>> ")

        # Store a second list of all attached vendor and product IDs
        with_attach = self.getDeviceIDs()

        # The difference of the lists is the attached device
        # Counter allows for multiple mice with the same IDs to be detected
        final.append(list((Counter(with_attach[0]) - Counter(guids[0])).elements()))
        final.append(list((Counter(with_attach[1]) - Counter(guids[1])).elements()))

        # Verify results
        result = self.verify_device(final, gui)

        if(result < 0):
            return result

        return (result[0], result[1])

    def verify_device(self, final, gui=0):
        ''' Verify a USB device was found '''

        flag = 0

        # More than one product or vendor ID recorded
        if(len(final[0]) > 1 or len(final[1]) > 1):
            flag = -1
            if(gui == 0):
                print("Multiple devices connected!")

        # No product and vendor ID recorded
        elif(len(final[0]) < 1 and len(final[1]) < 1):
            flag = -2
            if (gui == 0):
                print("No device detected!")

        # A product or vendor ID was detected without the other
        elif(len(final[0]) != len(final[1])):
            flag = -3
            if (gui == 0):
                print("Error. Vendor/Product ID Mismatch!")

        if(flag != 0):
            if(gui == 0):
                val = raw_input("Press Enter to restart or \'q\' to quit >>> ")
                if(val == 'q'):
                    return -1
                else:
                    return self.find_device()
            else:
                return flag

        return final

    def claim_device(self):
        ''' Claim the device from the kernel '''

       # Set endpoint
        self.endpoint = self.device[0][(0, 0)][0]

        # If the device is being used by the kernel
        if(self.device.is_kernel_driver_active(self.interface)) is True:
            self.device.detach_kernel_driver(self.interface)

        # Claim the device
        usb.util.claim_interface(self.device, self.interface)

    def read_thread_loop(self, event):
        ''' Reads data from a device until signaled. '''

        # Check for connected device
        if(self.prod_id == -1 or self.device == -1 or self.vendor == -1):
            print("No device attached!")
            return -1

        # Loop data read until interrupt
        while (event.is_set()):
            try:
                data_list = self.device.read(self.endpoint.bEndpointAddress, 8).tolist()

                # If data is in proper format, analyze movement
                if(len(data_list) == 8):
                    movement = Mouse_Movement(self.num, data_list)
                    self.movements.put(movement, block=False)

            except usb.core.USBError as error:
                if error.args == ('Operation timed out',):
                    continue

            # For keyboard interrupt
            except KeyboardInterrupt:
                print("Read interrupted by user. Exiting.")
                event.clear()
                return

    def print_thread_loop(self, devices, label, verbosity, event):
        ''' Thread to print readings from devices'''

        while (event.is_set()):
            movements = []
            for device in devices:
                if (device.movements.empty() is False):
                    movement = device.get_movement(label, verbosity)
                    if (movement is not None):
                        movements.append(movement)

            if (len(movements) > 0):
                print movements

    def read(self, devices=None, label=False, verbosity=2, gui=0):
        ''' Read one or more devices concurrently. If the label flag is set,
            the data read will be labeled by device'''

        # If no list passed
        if(devices is None):
            devices = [self]

        #If non list passed
        if(isinstance(devices, list) is False):
            return -1

        threads = []

        # Synchronize with event
        self.event.set()

        # Start and store all threads
        for device in devices:
            thread = Thread(target=device.read_thread_loop, args=(self.event,))
            threads.append(thread)
            thread.start()

        # Print if verbosity is greater than 0
        if(verbosity > 0):
            print_thread = Thread(target=device.print_thread_loop, args=(devices, label, verbosity, self.event,))
            threads.append(print_thread)
            print_thread.start()

        # Synchronized thread kill on keyboard interrupt (CTRL+C)
        try:
            while(1):
                if(gui == 1):
                    break

        except KeyboardInterrupt:
            print("Read interrupted by user. Exiting.")
            self.event.clear()
            [thread.join() for thread in threads]

    # Thanks to: https://stackoverflow.com/questions/11436502/closing-all-threads-with-a-keyboard-interrupt

    def read_all(self, label=True, verbosity=2):
        ''' Read all connected devices concurrently '''

        self.read(self.get_devices(), label, verbosity)

    def disconnect(self):
        ''' Release the device to the kernel '''

        # Check for connected device
        if(self.prod_id == -1 or self.device == -1 or self.vendor == -1):
            print("No device attached!")
            return -1

        # Release device
        usb.util.release_interface(self.device, self.interface)

        if(self.device.is_kernel_driver_active(self.interface)) is False:
            self.device.attach_kernel_driver(self.interface)

        # Remove from shared connected device list and adjust indices
        for device in range(self.index + 1, self.num_con_devices):
            USB_Mouse.con_devices[device].index -= 1

        USB_Mouse.num_con_devices -= 1

        del USB_Mouse.con_devices[self.index]

        # Reinitialize for reuse
        print("Device " + str(self.num) + " disconnected")

        self.__init__()

    def get_info(self):
        ''' Return info '''

        return [("Number", self.num), ("Index", self.index),
                ("Product_ID", self.prod_id),
                ("Vendor_ID", self.vendor),
                ("Total_Devices", USB_Mouse.num_con_devices)]

    def get_movement(self, label=False, verbosity=2):
        ''' Get the current movement '''

        # If verbosity is 1
        # Return raw data
        if(verbosity == 1):
            movement = self.movements.get(block=False).get_raw(label)
            return movement

        # If verbosity is 2
        # Return verbose data
        elif(verbosity == 2):
            movement = self.movements.get(block=False).get_data(label)
            return movement

    def get_devices(self):
        ''' Return a list of all USB_Mouse objects paired with a physical device'''

        return USB_Mouse.con_devices
