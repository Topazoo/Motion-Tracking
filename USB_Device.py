#!/usr/bin/python

''' Author: Peter Swanson
            pswanson@ucdavis.edu

    Description: Class to track optical mouse motion via USB. Can track data from multiple
    mice concurrently.

    Version: Python 2.7

    Methods inspired by:
    https://www.orangecoat.com/how-to/use-pyusb-to-find-vendor-and-product-ids-for-usb-devices
    https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack
    https://stackoverflow.com/questions/21731043/use-of-input-raw-input-in-python-2-and-3 '''

from collections import Counter
from threading import Thread
import usb.core
import usb.util

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

    def attach(self):
        ''' Take control of the device and read data '''

        # Find the device to attach to
        ids = self.find_device()

        if(ids == -1):
            print("Failed to connect to a device...")
            return -1

        self.vendor = ids[0][0]
        self.prod_id = ids[1][0]
        self.device = usb.core.find(idVendor=self.vendor, idProduct=self.prod_id)

        # Take control from the kernel
        self.claim_device()

        # Check success
        if (self.prod_id == -1 or self.device == -1 or self.vendor == -1):
            print("No device attached!")
            return -1

        # Update shared number of connected devices
        self.num = USB_Mouse.num_con_devices
        USB_Mouse.num_con_devices += 1

        # Store device so all connected devices can be accessed with one object
        USB_Mouse.con_devices.append(self)
        self.index = len(self.con_devices) - 1

        print("Device " + str(self.num) + " attached!")

        return 0

    def find_device(self):
        ''' Find a USB device '''

        all_ids = [[], []]
        with_attach = [[], []]
        final = []

        raw_input("Ensure the USB device you want to track is detached and press Enter >>> ")

        # Get all connected devices
        devices = usb.core.find(find_all=True)

        # Store a list of all attached vendor and product IDs
        for cfg in devices:
            all_ids[0].append(int(cfg.idVendor))
            all_ids[1].append(int(cfg.idProduct))

        raw_input("Please attach the USB device and press Enter >>> ")

        # Store a second list of all attached vendor and product IDs
        devices = usb.core.find(find_all=True)

        for cfg in devices:
            with_attach[0].append(int(cfg.idVendor))
            with_attach[1].append(int(cfg.idProduct))

        # The difference of the lists is the removed device
        final.append(list((Counter(with_attach[0]) - Counter(all_ids[0])).elements()))
        final.append(list((Counter(with_attach[1]) - Counter(all_ids[1])).elements()))

        # Verify results
        result = self.verify_device(final)

        if(result == -1):
            return result

        return (result[0], result[1])

    def verify_device(self, final):
        ''' Verify a USB device was found '''

        flag = 0

        # More than one product or vendor ID recorded
        if(len(final[0]) > 1 or len(final[1]) > 1):
            flag = 1
            print("Multiple devices connected.")

        # No product and vendor ID recorded
        elif(len(final[0]) < 1 and len(final[1]) < 1):
            flag = 1
            print("No device detected.")

        # A product or vendor ID was detected without the other
        elif(len(final[0]) != len(final[1])):
            flag = 1
            print("Error. Vendor/Product ID Mismatch.")

        if(flag == 1):
            val = raw_input("Press Enter to restart or \'q\' to quit >>> ")

            if(val == 'q'):
                return -1
            else:
                return self.find_device()

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

        return 0

    def read(self, label = 0):
        ''' Read data from the device '''

        # Check for connected device
        if(self.prod_id == -1 or self.device == -1 or self.vendor == -1):
            print("No device attached!")
            return -1

        data_list = []

        # Loop data read until interrupt
        while (1):
            try:
                data_list = self.device.read(self.endpoint.bEndpointAddress, 8).tolist()

                # Normalize data array size
                if(len(data_list) == 8):
                    # If data should be labeled
                    if(label == 1):
                        data_list = ("Device: " + str(self.num), data_list)

                    print(data_list)

            except usb.core.USBError as error:
                if error.args == ('Operation timed out',):
                    continue

            except KeyboardInterrupt:
                print("Keyboard interrupt during data read")
                return 0

    def threaded_read(self, label=0):
        ''' Thread wrapper for read() '''

        # Run a thread of this object's read() function
        thread = Thread(target=self.read, args=(label,))
        thread.start()

        return thread

    def read_multiple(self, devices, label=0):
        ''' Read multiple devices concurrently '''

        if(isinstance(devices, list) is False):
            print("A list of devices was not passed to the function...")
            return -1

        threads = []

        # Start and store all threads
        for device in devices:
            threads.append(device.threaded_read(label))

        return 0

    def read_all(self, label=0):
        ''' Read all connected devices concurrently '''

        self.read_multiple(self.get_devices(), label)

    def release(self):
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
        print("Device " + str(self.num) + " released!")

        self.__init__()

        return 0

    def get_info(self):
        ''' Return info:
            num
            index
            prod_id
            vendor
            num_con_devices '''

        return (self.num, self.index, self.prod_id, self.vendor, USB_Mouse.num_con_devices)

    def get_devices(self):
        ''' Return a list of all USB_Mouse objects paired with a physical device'''

        return USB_Mouse.con_devices
