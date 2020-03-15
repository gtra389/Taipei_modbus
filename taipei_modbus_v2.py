#!/usr/bin/env python
#
# Aailable device: Tipping-bucket Rain gauge
# Product number: SMR29-C
# Serial communication protocol: Pulse(interrupt function)
# Purpose:
# Measure rainfall intensity every 10 mins (Unit in mm/hr)
# Address of slave: N/A

#
# Available device: Liquid level sensor
# Manufacturer: AQUAS Inc.
# Product number: SMR02
# Serial communication protocol: RS485
# Purpose:
# Measure ground water level every 10 mins (Unit in meter)
#

# Including
import time
import RPi.GPIO as GPIO
from statistics import median
import minimalmodbus
import urllib3


# Definition of variable
minimalmodbus.BAUDRATE = 19200
wL_slaveAddr = 1
devName = '/dev/ttyUSB0' # RPI    format
comName = 'COM5'        # Window format
wl_id_No = "6001"
rg_id_No = "8001" # Songde North: 8001

BUTTON_PIN = 14   # Use GPIO 14 as a interrupt pin

bucketNum = 0
timeIntval = 600  # Unit in second
bucketVal = 0.2  # Unit in mm
rfInts    = 0    # Unit in mm/hr
rfDep     = 0    # Unit in mm

# Variable of the water level sensor
slope = 0.04626
intercept = -760.80073

rebootFlag = True

def my_callback(channel):
    global bucketNum
    bucketNum += 1
    print("Bucket dectected")
    print("Bucket Number: {}".format(bucketNum))
    #print("Time: {}".format(time.strftime("%Y%m%d%H%M%s")))
    print("------------------------------")
    time.sleep(0.1)

def httpPOST(String0, String1, String2, String3):    
    try:
        global timeStamp
        timeStamp = time.strftime("%Y%m%d%H%M%S")
        url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?' + \
              'site=Demo&' + \
              'time='+ str(timeStamp)+ \
              '&weather=0' + \
              '&id='+ str(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+str(String1)+ \
              '&field2='+str(String2)+ \
              '&field3='+repr(String3)
       
        url_TT ='http://data.thinktronltd.com/TCGEMSIS/GETMTDATA.aspx?' + \
              'site=Demo&' + \
              'time='+ str(timeStamp)+ \
              '&weather=0' + \
              '&id='+ str(String0) + \
              '&air=0' + \
              '&acceleration=0' + \
              '&cleavage=0' + \
              '&incline=0' + \
              '&field1='+str(String1)+ \
              '&field2='+str(String2)+ \
              '&field3='+repr(String3) 
        
        #resp = urlopen(url).read()
        #resp_TT = urlopen(url_TT).read()
	#print("URL: {}".format(url))
	
        http = urllib3.PoolManager()
        resp = http.request('POST', url)
        resp_TT = http.request('POST', url_TT)

        print("{} AWS Statue: {}".format(String0, resp.status))
        print("{} TT  Statue: {}".format(String0, resp_TT.status))
        print('------------------------')
    except:
        print('We have an error!')
        time.sleep(5) # Wait for 30 sec
        #resp = urlopen(url).read()
        #print(resp)
        http = urllib3.PoolManager()
        resp = http.request('POST', url)
        resp_TT = http.request('POST', url_TT)

        print("Try again!")
        print("{} AWS Statue: {}".format(String0, resp.status))
        print("{} TT  Statue: {}".format(String0, resp_TT.status))
        print('------------------------')

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
        wLVal = 9999
        print("Failed to read from instrument")
        print('------------------------')
        
    return wLVal


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback = my_callback, bouncetime = 500)

startTime = time.time()
endTime   = time.time()

try:
    while rebootFlag:
        # Reboot for the raingage
        data1 = 0 
        data2 = 0
        httpPOST(rg_id_No, data1, data2, "Reboot")

        # Reboot for the water level sensor
        data1 = wLRead(slope, intercept)
        data2 = 0
        httpPOST(wl_id_No, data1, data2, "Reboot")

        # Reset the Variable
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        rebootFlag = False

    while True:
      if ( endTime - startTime > timeIntval ):
        print("Send mesg.")

        # Upload value from the raingage
        rfDep  = bucketNum * bucketVal
        rfInts = rfDep/0.1666667 # Unit in mm/hr every 10 mins        
        data1 = round(rfInts,3) 
        data2 = 0
        httpPOST(rg_id_No, data1, data2, 0)

        # Upload value from the water level sensor
        data1 = wLRead(slope, intercept)
        data2 = 0
        httpPOST(wl_id_No, data1, data2, 0)

        # Reset the Variable
        data1 = 0
        data2 = 0
        bucketNum = 0
        startTime = endTime
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL=True
        time.sleep(0.1)

      endTime = time.time()
      # print("Time interval: {} ".format(endTime - startTime))
      time.sleep(0.5)      
except KeyboardInterrupt:
    print("Shut down!")
finally:
    GPIO.cleanup()
