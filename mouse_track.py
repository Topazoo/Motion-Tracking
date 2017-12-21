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
        USB_Device.curr_devices += 1

        # Create instance variables
        self.prod_id = -1
        self.vendor = -1
        self.device = -1
        self.endpoint = -1

        # Store device so all devices can be accessed with one object
        USB_Device.list_devices.append(self)

    def read(self):
        ''' Take control of the device and read data '''

        # Find the device to attach to
        ids = self.find_device()
        self.vendor = ids[0][0]
        self.prod_id = ids[1][0]
        self.device = usb.core.find(idVendor=self.vendor, idProduct=self.prod_id)

        # Take control from the kernel
        self.claim_device()

        # Read device
        self.read_device()

        # Release control
        self.release_device()

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

        raw_input("Please reattach the USB device and press Enter >>> ")

        # Store a second list of all attached vendor and product IDs
        devices = usb.core.find(find_all=True)

        for cfg in devices:
            with_attach[0].append(int(cfg.idVendor))
            with_attach[1].append(int(cfg.idProduct))

        # The difference of the lists is the removed device
        final.append(list(set(with_attach[0]) - set(all_ids[0])))
        final.append(list(set(with_attach[1]) - set(all_ids[1])))

        # Verify results
        result = self.verify_device(final)

        return (result[0], result[1])

    def verify_device(self, final):
        ''' Verify a USB device was found '''

        if(len(final[0]) > 1 or len(final[1]) > 1):
            raw_input("Multiple devices connected. Press Enter to restart >>> ")
            return self.find_device()
        elif(len(final[0]) < 1 or len(final[1]) < 1):
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

    def read_device(self):
        ''' Read data drom the device'''

        data_list = []

        while (1):
            try:
                data_list = self.device.read(self.endpoint.bEndpointAddress,
                                             self.endpoint.wMaxPacketSize).tolist()
                print(data_list)

            except KeyboardInterrupt:
                print("Keyboard interrupt during data read")
                print("Releasing device to kernel and exiting...")
                self.release_device()
                sys.exit(0)

            except usb.core.USBError as error:
                if error.args == ('Operation timed out',):
                    continue

    def release_device(self):
        ''' Release the device to the kernel '''

        usb.util.release_interface(self.device, self.interface)
        self.device.attach_kernel_driver(self.interface)

    def get_info(self):
        ''' Return device info '''

        return (self.interface, self.prod_id, self.vendor)

def main():
    ''' Main driver '''

    device = USB_Device()
    device.read()

if __name__ == "__main__":
    main()
