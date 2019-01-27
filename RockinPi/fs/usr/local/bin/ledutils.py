#!/usr/bin/env python

import time, pibrella

def driveLED(led, val):
    if val:
        led.on()
    else:
        led.off()

def driveLEDs(green, amber, red):
    driveLED(pibrella.light.green, green)
    driveLED(pibrella.light.amber, amber)
    driveLED(pibrella.light.red, red)

def ledGreeting():
    pibrella.light.red.fade(0, 100, 2)
    pibrella.light.amber.fade(0, 100, 2)
    pibrella.light.green.fade(0, 100, 2)
    time.sleep(1)
    pibrella.light.red.fade(100, 0, 2)
    pibrella.light.amber.fade(100, 0, 2)
    pibrella.light.green.fade(100, 0, 2)
    time.sleep(1)
    driveLEDs(False, False, False)
