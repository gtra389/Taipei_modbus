#!/usr/bin/env python
#
# Available device: Tipping-bucket Rain gauge
# Product number: SMR29-C
# Serial communication protocol: RS485
# Purpose:
# Test the comunication between devices and loggers
#

# Including
import minimalmodbus
import time
import RPi.GPIO as GPIO

# Setting RS485 CAN HAT
EN_485 =  4
GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_485,GPIO.OUT)
GPIO.output(EN_485,GPIO.HIGH)

# Definition of variable
minimalmodbus.BAUDRATE = 19200
rg_slaveAddr = 2
# devName = '/dev/ttyUSB0' # RPI  format via USB
devName = "/dev/serial0" # pi zero
# devName = "/dev/ttyS0"   # using RPI via  RS485 CAN HAT # Raspberry Pi 3B+
# comName = 'COM3'         # Window format

try:
    while True:
        instrument_2 = minimalmodbus.Instrument(devName, rg_slaveAddr)
        #instrument_2 = minimalmodbus.Instrument(comName, rg_slaveAddr) 
        # Register number, number of decimals, function code
        rf_realVal = instrument_2.read_register(0, 0, 4)
        print("rf_readVal: {}".format(rf_realVal))
        instrument_2.close_port_after_each_call = True
        time.sleep(1) # Wait for 1 second
except KeyboardInterrupt:
    print("Stop!")
    instrument_2.close_port_after_each_call = True
    break