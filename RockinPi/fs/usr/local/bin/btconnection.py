#/usr/bin/env python

import bluetooth

class BluetoothConnection:
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def connect(self):
        self.sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect((self.addr, self.port))

    def disconnect(self):
        self.sock.close()

    def send(self, msg):
        self.sock.send(msg)
