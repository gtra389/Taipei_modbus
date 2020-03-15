#!/bin/bash

# sleep 15
# sudo python /home/pi/Taipei_modbus/LLS_RG_modbus_taipei.py
# sudo python /home/pi/Taipei_modbus/raingage_interrupt.py
# while :
# do
if [ `ps -U root -u root u | grep python | wc -m` -eq 0 ]
  then 
    sudo python /home/pi/Taipei_modbus/taipei_modbus_v2.py
    sleep 1
  else
    sleep 1
fi
# done
