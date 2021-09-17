#! /bin/bash
# script to flash esp8266 based nodemcu


FIRMWARE_NAME='esp8266-micropython.bin'
FIRMWARE_URL='https://micropython.org/resources/firmware/esp8266-1m-20200902-v1.13.bin'
DEVICE=$1


# download firmware
mkdir -p "/tmp"
if [ ! -e "/tmp/$FIRMWARE_NAME" ]; then
    wget $FIRMWARE_URL -O "/tmp/$FIRMWARE_NAME"
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
        echo "Erasing old firmware..."
        esptool.py --port /dev/ttyUSB0 erase_flash
        esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 "/tmp/$FIRMWARE_NAME"
    fi
fi