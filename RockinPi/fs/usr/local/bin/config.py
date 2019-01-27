#!/usr/bin/env python

import json

class RockinPiConfig:
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.datastore = json.load(f)

    def getBluetoothDeviceAddress(self):
        return self.datastore['bluetooth.device.address']

    def getBluetoothPort(self):
        return int(self.datastore['bluetooth.port'])

    def getWorkerSleepTime(self):
        return int(self.datastore['worker.sleep.time'])
