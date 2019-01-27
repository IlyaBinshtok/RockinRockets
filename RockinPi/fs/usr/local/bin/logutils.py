#!/usr/bin/env python
#import os, subprocess
from globalvars import logfile

def logMessage(message):
    f = open(logfile, "a")
    f.write(message+'\n')
    f.flush
    f.close()

def logAndPrintMessage(message):
    print message
    f = open(logfile, "a")
    f.write(message+'\n')
    f.flush
    f.close()
