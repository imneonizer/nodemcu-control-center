#! /bin/bash
# script to work with esp8266 based nodemcu

if [[ $1 == /dev/ttyUSB* ]] ;then
    DEVICE="$1"
else
    DEVICE="/dev/ttyUSB$1"
fi

# install dev tools: esptool, adafruit-ampy
if [ "`pip -V`" ];then
    # check esptool.py
    if [ ! "`pip freeze | grep -i esptool`" ];then
        pip install esptool.py
    fi

    # check ampy
    if [ ! "`pip freeze | grep -i adafruit-ampy`" ];then
        pip install adafruit-ampy
    fi
else
    echo "pip not found"
    exit -1
fi