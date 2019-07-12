#!/bin/bash

sleep 15
sudo python /home/pi/Taipei_modbus/LLS_modbus_taipei.py >> log
while :
do
  if [ `ps -U root -u root u | grep python | wc -m` -eq 0 ]
  then 
    sudo python sudo python /home/pi/Taipei_modbus/LLS_modbus_taipei.py >> log
    sleep 180
  else
    sleep 180
  fi
done
