#!/usr/bin/env python
#
# Available device: Liquid level sensor
# Manufacturer: Han Da
# Product number: IPL900
# Serial communication protocol: RS485
# Purpose:
# Measure ground water level every 10 mins (Unit in meter)
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
minimalmodbus.BAUDRATE = 9600
wL_slaveAddr = 1
devName = "/dev/ttyS0" # using RPI via  RS485 CAN HAT # Raspberry Pi 3B+

# classminimalmodbus.Instrument(port, slaveaddress, mode='rtu', close_port_after_each_call=False, debug=False)
instrument_wL = minimalmodbus.Instrument(devName, wL_slaveAddr, 'rtu')

while True:
    try:
        fullScale = instrument_wL.read_registers(0x6,1,3)
        fullScalePys = 10 # Unit in mH2O
        # Register address / Number of registers / Function code
        wLvalue = instrument_wL.read_registers(0x4,1,3)
        # print("wLvalue: {}".format(wLvalue[0]))
        wLvaluePys = wLvalue[0]*10/fullScale[0]
        print("wLvalue: {} mH2O".format(wLvaluePys))
        time.sleep(1) # Wait for 1 second
    except:
        print("Stop!")
        instrument_wL.close_port_after_each_call = True
        break

