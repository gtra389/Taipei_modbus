#!/bin/bash

sleep 15
sudo python /home/pi/Taipei_modbus/LLS_RG_modbus_taipei >> log
while :
do
  if [ `ps -U root -u root u | grep python | wc -m` -eq 0 ]
  then 
    sudo python /home/pi/Taipei_modbus/LLS_RG_modbus_taipei >> log
    sleep 180
  else
    sleep 180
  fi
done
