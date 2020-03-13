#!/usr/bin/env python
#
# Available device: Liquid level sensor
# Manufacturer: AQUAS Inc.
# Product number: SMR02
# Serial communication protocol: RS485
# Purpose:
# Measure ground water level every 10 mins (Unit in meter)
#

# Including
from statistics import median
import minimalmodbus
import time
from time import gmtime, strftime
# from urllib.request import urlopen
from urllib2 import urlopen

# Definition of variable
minimalmodbus.BAUDRATE = 19200
wL_slaveAddr = 1
devName = '/dev/ttyUSB0' # RPI    format
comName = 'COM5'        # Window format
id_No = "6003"
countNum_Loop = -1

def wLRead(slp,intcpt): 
    # Port name, slave address (in decimal)
    # instrument_wL = minimalmodbus.Instrument(comName, wL_slaveAddr) 
    instrument_wL = minimalmodbus.Instrument(devName, wL_slaveAddr)
    try:
        samplingList = []
        medianVal = 0
        countNum  = 0
        sampleNum = 10
        while (countNum <= sampleNum): 
            # Register address / Number of registers / Function code
            ReadingValue = instrument_wL.read_registers(0,2,4)
            power = len(str(ReadingValue[0]))
            ArrangeValue = ReadingValue[1] + ReadingValue[0]/(10**power)
            samplingList.append(ArrangeValue)
            countNum += 1
            print(countNum)
            time.sleep(1) # Wait for 1 second
            
        medianVal = median(samplingList)
        wLVal     = round(slp * medianVal + intcpt, 3)
        
        idn = instrument_wL.read_register(1, 0, 3)
        print('-----Liquid level sensor-----')
        print('id = '+str(idn))
        print('water level = ' + str(wLVal) + ' m')                
             
    except IOError:
        wLVal = 0
        print("Failed to read from instrument")
        print('------------------------')
        
    return wLVal

def httpPOST(String0, String1, String2, String3):    
    try:
        global timeStamp
        timeStamp = strftime("%Y%m%d%H%M%S")
        url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?' + \
              'site=Demo&' + \
              'time='+ repr(timeStamp)+ \
              '&weather=0' + \
              '&id='+ repr(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+repr(String1)+ \
              '&field2='+repr(String2)+ \
              '&field3='+repr(String3)
        
        url_TT ='http://data.thinktronltd.com/TCGEMSIS/GETMTDATA.aspx?' + \
              'site=Demo&' + \
              'time='+ repr(timeStamp)+ \
              '&weather=0' + \
              '&id='+ repr(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+repr(String1)+ \
              '&field2='+repr(String2)+ \
              '&field3='+repr(String3) 
        
        resp = urlopen(url).read()
        resp_TT = urlopen(url_TT).read()
        print(resp)
        print(resp_TT)
        print('------------------------')
    except:
        print('We have an error!')
        time.sleep(30) # Wait for 30 sec
        resp = urlopen(url).read()
        print(resp)
        print('------------------------')
    
try:
    while True:
        slope = 0.04626
        intercept = -760.80073
        data1 = wLRead(slope, intercept)
        data2 = 0
        
        while (countNum_Loop < 0):
            httpPOST(id_No, data1, data2, "Reboot")
            countNum_Loop += 1
            
        if countNum_Loop == -1:
            break
            
        httpPOST(id_No, data1, data2, 0)            
        
        print("Upload time : %s" % timeStamp)        
        print('------------------------')
        
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        time.sleep(60*10) # Wait for 10 mins
        
except KeyboardInterrupt:
    print('------------------------')
    print("Stop")
    print('------------------------')
