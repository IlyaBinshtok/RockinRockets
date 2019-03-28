#/usr/bin/env python

import bluetooth

# This devines a BT scan class
class BluetoothScan:

    # BluetoothScan constructor that takes a list of available 
    # HC-05 devices obtained form the rockinPi.conf file   
    def __init__(self, devices):
        self.hc05Devices = devices

    # This method does BT discovery to obtain a list of all BT devices nearby and
    # checks if any of those devices are listed in the rockinPi.conf file. The list
    # discovered HC-05 devices listed in the rockinPi.conf is returned.
    def discover(self):
        ret = []
        discoveredBtDevices = bluetooth.discover_devices()
        for discoveredBtDevice in discoveredBtDevices:
            if discoveredBtDevice in self.hc05Devices:
                ret.append(discoveredBtDevice)
        return ret
