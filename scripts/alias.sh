#! /bin/bash
# script to work with esp8266 based nodemcu

DEVICE=$1

# check if script is being sourced
if [[ ! "${BASH_SOURCE[0]}" != "${0}" ]];then
    echo "Usage: source $0"
    exit
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

    # check rshell
    if [ ! "`pip freeze | grep -i rshell`" ];then
        pip install rshell
    fi
else
    echo "pip not found"
    exit -1
fi

# validate device
if [ ! "$DEVICE" ]; then
    echo "No port provided, choose one:"
    echo "`ls /dev/ttyUSB*`"
else
    if [ ! "`ls $DEVICE`" ];then
        echo "Device not found: $DEVICE"
    else
        echo "Using: $DEVICE"
        export AMPY_PORT=$DEVICE
        export AMPY_BAUD=115200
        alias mcu="picocom -b $AMPY_BAUD $AMPY_PORT"
    fi
fi