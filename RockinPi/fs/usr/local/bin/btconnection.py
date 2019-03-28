#/usr/bin/env python

import bluetooth

# This class defines bluetooth connection
class BluetoothConnection:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    # connects to bluetooth device
    def connect(self):
        self.sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.addr, self.port))
    
    # disconnects from bluetooth device
    def disconnect(self):
        self.sock.close()

    # sends supplied message to bluetooth device 
    def send(self, msg):
        self.sock.send(msg)

    # reports bluetooth address of the device
    def getAddress(self):
        return self.addr

    # reports bluetooth port
    def getPort(self):
        return self.port
