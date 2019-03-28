#!/usr/bin/env python

import sys, os, time, signal, pibrella, threading, bluetooth
from globalvars import enum, logfile
from logutils import logMessage
from btscan import BluetoothScan
from btconnection import BluetoothConnection
from ledutils import driveLEDs, ledGreeting
from config import RockinPiConfig

EmsType = enum(NA=0, OFF=1, INTERFERANCE=2, RUSSIAN=3)
EmsOutType = enum(OFF='0', INTERFERANCE='1', RUSSIAN='2')
emsType = EmsType.NA

configFile = '/usr/local/bin/rockinPi.conf'
pressTime = 0
buttonEventTime = 0
systemOn = False
onTimer = None
offTimer = None
ignoreButtonEvent = False
btConnections = []

def worker():
    while systemOn:
        if emsType is EmsType.INTERFERANCE:
            for btConnection in btConnections:
                btConnection.send(EmsOutType.INTERFERANCE)
        elif emsType is EmsType.RUSSIAN:
            for btConnection in btConnections:
                btConnection.send(EmsOutType.RUSSIAN)
        else:
            for btConnection in btConnections:
                btConnection.send(EmsOutType.OFF)
        time.sleep(config.getWorkerSleepTime())

def turnOn():
    global systemOn
    global onTimer
    global emsType
    global workerThread
    global btConnections
    if systemOn:
        logMessage("turnOn() :: system is already ON")
        return
    logMessage("turnOn() :: Turning ON ...")
    driveLEDs(False, False, True)
    if onTimer is not None:
        onTimer.cancel()
        onTimer = None
    systemOn = True
    emsType = EmsType.NA
    try:
        pibrella.light.green.blink(0.5, 0.5)
        btDevices = BluetoothScan(config.getBluetoothDevices()).discover()
        logMessage("turnOn() :: btDevices={}".format(btDevices))
        for btDevice in btDevices: 
            btConnection = BluetoothConnection(btDevice, config.getBluetoothPort())
            btConnection.connect()
            btConnections.append(btConnection)
            logMessage("turnOn() :: BT connection to {} is ON !!!".format(btDevice))
        workerThread = threading.Thread(target=worker)
        workerThread.start()
        driveLEDs(False, False, True)
    except bluetooth.btcommon.BluetoothError as e:
        pibrella.light.amber.blink(0.5,0.5)
        pibrella.light.green.blink(0.5,0.5)
        logMessage("turnOn() :: BT Exception: {}".format(e)) 

def turnOff():
    global systemOn
    global offTimer
    global emsType
    global workerThread
    global ignoreButtonEvent
    global btConnections
    if not systemOn:
        logMessage("turnOff() :: system is already OFF")
        return
    logMessage("turnOff() :: turning OFF ...")
    ignoreButtonEvent = True
    driveLEDs(False, False, False)
    if offTimer is not None:
        offTimer.cancel()
        offTimer = None
    emsType = EmsType.NA
    pibrella.light.red.blink(1,1)
    time.sleep(3*config.getWorkerSleepTime())
    driveLEDs(False, False, False)
    systemOn = False;
    for btConnection in btConnections:
        btConnection.disconnect()
        btConnections.remove(btConnection)
        logMessage("turnOff() :: BT connection to {} is OFF !!!".format(btConnection.getAddress()))
    ignoreButtonEvent = False

def button_event(pin):
    global buttonEventTime
    global onTimer
    global offTimer
    global emsType
    global ignoreButtonEvent
    if ignoreButtonEvent:
        logMessage("button_event() :: ignoring this button event")
        return
    ignoreButtonEvent = True
    currentTime = time.time()
    buttonInput = pibrella.button.read()
    logMessage("button_event() :: button-input={}".format(buttonInput))
    #if buttonEventTime > 0:
    if buttonInput == 0:
        #button released
        logMessage("button_event() :: button released in {} sec.".format(currentTime - buttonEventTime))
        if onTimer is not None:
            onTimer.cancel()
            onTimer = None
        if offTimer is not None:
            offTimer.cancel()
            offTimer = None
        if systemOn:
            if emsType is EmsType.NA:
                emsType = EmsType.OFF
            elif emsType is EmsType.OFF:
                emsType = EmsType.INTERFERANCE
                driveLEDs(False, True, True)
                logMessage("button_event() :: EMS Type: INTERFERANCE" )
            elif emsType is EmsType.INTERFERANCE:
                emsType = EmsType.RUSSIAN
                driveLEDs(True, False, True)
                logMessage("button_event() :: EMS Type: RUSSIAN")
            elif emsType is EmsType.RUSSIAN:
                emsType = EmsType.OFF
                driveLEDs(False, False, True)
                logMessage("button_event() :: EMS Type: OFF")
        buttonEventTime = 0
    else:
        # button pressed
        logMessage("button_event() :: button pressed")
        buttonEventTime = currentTime
        if systemOn:
            offTimer = threading.Timer(5.0, turnOff)
            offTimer.start()
        else:
            onTimer = threading.Timer(5.0, turnOn)
            onTimer.start()
    ignoreButtonEvent = False

f = open(logfile, "w")
f.close()
config = RockinPiConfig(configFile)
logMessage("Starting rockinPi ...")
logMessage("config :: BT device address={}".format(config.getBluetoothDevices()))
logMessage("config :: BT port={}".format(config.getBluetoothPort()))
logMessage("config :: worker thread sleep time: {} sec.".format(config.getWorkerSleepTime()))
ledGreeting()
logMessage("rockingPi is running !!! Press and hold a button for 5 seconds to begin ...")
pibrella.button.changed(button_event)
signal.pause()
