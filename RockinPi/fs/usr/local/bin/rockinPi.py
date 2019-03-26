#!/usr/bin/env python

import sys, os, time, signal, pibrella, threading, bluetooth
from globalvars import enum, logfile
from logutils import logMessage
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

def worker():
    while systemOn:
        if emsType is EmsType.INTERFERANCE:
            btConnection.send(EmsOutType.INTERFERANCE)
        elif emsType is EmsType.RUSSIAN:
            btConnection.send(EmsOutType.RUSSIAN)
        else:
            btConnection.send(EmsOutType.OFF)
        time.sleep(config.getWorkerSleepTime())

def turnOn():
    global systemOn
    global onTimer
    global emsType
    global btConnection
    global workerThread
    logMessage("turnOn() :: Turning ON ...")
    driveLEDs(False, False, True)
    onTimer.cancel()
    onTimer = None
    systemOn = True
    emsType = EmsType.NA
    try:
        btConnection = BluetoothConnection(config.getBluetoothDeviceAddress(), config.getBluetoothPort())
        btConnection.connect()
        workerThread = threading.Thread(target=worker)
        workerThread.start()
        logMessage("turnOn() :: BT connection is ON !!!")
    except bluetooth.btcommon.BluetoothError as e:
        pibrella.light.amber.blink(0.5,0.5)
        pibrella.light.green.blink(0.5,0.5)
        logMessage("turnOn() :: BT Exception: {}".format(e)) 

def turnOff():
    global systemOn
    global offTimer
    global emsType
    global workerThread
    logMessage("turnOff() :: turning OFF ...")
    driveLEDs(False, False, False)
    offTimer.cancel()
    offTimer = None
    emsType = EmsType.NA
    pibrella.light.red.blink(1,1)
    time.sleep(3*config.getWorkerSleepTime())
    driveLEDs(False, False, False)
    systemOn = False;
    btConnection.disconnect()
    logMessage("turnOff() :: BT connection is OFF !!!")

def button_event(pin):
    global buttonEventTime
    global onTimer
    global offTimer
    global emsType
    currentTime = time.time()
    buttonInput = pibrella.button.read()
    logMessage("button-input={}".format(buttonInput))
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

f = open(logfile, "w")
f.close()
config = RockinPiConfig(configFile)
logMessage("Starting rockinPi ...")
logMessage("config :: BT device address={}".format(config.getBluetoothDeviceAddress()))
logMessage("config :: BT port={}".format(config.getBluetoothPort()))
logMessage("config :: worker thread sleep time: {} sec.".format(config.getWorkerSleepTime()))
ledGreeting()
logMessage("rockingPi is running !!! Press and hold a button for 5 seconds to begin ...")
pibrella.button.changed(button_event)
signal.pause()
