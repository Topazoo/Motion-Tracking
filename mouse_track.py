#!/usr/bin/python

''' Author: Peter Swanson
    Description: Track optical mouse motion via USB

    Version: Python 2.7

    Methods inspired by:
    https://www.orangecoat.com/how-to/use-pyusb-to-find-vendor-and-product-ids-for-usb-devices
    https://www.orangecoat.com/how-to/read-and-decode-data-from-your-mouse-using-this-pyusb-hack
    https://stackoverflow.com/questions/21731043/use-of-input-raw-input-in-python-2-and-3'''

import sys
import usb.core
import usb.util
from collections import Counter

class USB_Device(object):
    ''' USB Device object that holds information needed
        find and interface with a USB device '''

    # Class Variables - (Shared by all instances)
    curr_devices = 0
    list_devices = []

    def __init__(self):
        ''' Construct a device object with a product and
            device ID. Automatically assign interface number '''

        # Set and update class variables
        self.interface = USB_Device.curr_devices

        # Create instance variables
        self.prod_id = -1
        self.vendor = -1
        self.device = -1
        self.endpoint = -1

        # Store device so all devices can be accessed with one object
        USB_Device.list_devices.append(self)

    def attach(self):
        ''' Take control of the device and read data '''

        # Find the device to attach to
        ids = self.find_device()
        self.vendor = ids[0][0]
        self.prod_id = ids[1][0]
        self.device = usb.core.find(idVendor=self.vendor, idProduct=self.prod_id)

        # Take control from the kernel
        self.claim_device()

        if(self.prod_id == -1 or self.device == -1 or self.endpoint == -1 or
           self.vendor == -1):
           print("No device attached!")
           return -1

        USB_Device.curr_devices += 1
        
        print("Device " + str(self.prod_id) + " attached!")

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

        return (result[0], result[1])

    def verify_device(self, final):
        ''' Verify a USB device was found '''

        if(len(final[0]) > 1 or len(final[1]) > 1):
            raw_input("Multiple devices connected. Press Enter to restart >>> ")
            return self.find_device()
        elif(len(final[0]) < 1 and len(final[1]) < 1):
            raw_input("No device detected. Press Enter to restart >>> ")
            return self.find_device()
        elif(len(final[0]) != len(final[1])):
            raw_input("Error. Vendor/Product ID Mismatch. Press Enter to restart >>> ")
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

    def read(self):
        ''' Read data drom the device'''

        if(self.prod_id == -1 or self.device == -1 or self.endpoint == -1 or
           self.vendor == -1):
           print("No device attached!")
           return -1

        data_list = []

        while (1):
            try:
                data_list = self.device.read(self.endpoint.bEndpointAddress,
                                             self.endpoint.wMaxPacketSize).tolist()
                print(data_list)

            except usb.core.USBError as error:
                if error.args == ('Operation timed out',):
                    continue

            except KeyboardInterrupt:
                print("Keyboard interrupt during data read")
                break

    def release(self):
        ''' Release the device to the kernel '''

        if(self.prod_id == -1 or self.device == -1 or self.endpoint == -1 or
           self.vendor == -1):
           print("No device attached!")
           return -1

        usb.util.release_interface(self.device, self.interface)
        
        if(self.device.is_kernel_driver_active(self.interface)) is False:
            self.device.attach_kernel_driver(self.interface)

        print("Device " + str(self.prod_id) + " released!")

        self.device = -1
        self.endpoint = -1
        self.vendor = -1
        self.prod_id = -1

        USB_Device.curr_devices -= 1



    def get_info(self):
        ''' Return device info '''

        return (self.interface, self.prod_id, self.vendor)

def main():
    ''' Main driver '''

    device = USB_Device()
    device.attach()
    device.read()

if __name__ == "__main__":
    main()
