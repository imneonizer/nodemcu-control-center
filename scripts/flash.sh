#! /bin/bash
# script to flash esp8266 based nodemcu
# sudo usermod -a -G dialout $USER

FIRMWARE_NAME='esp8266-micropython.bin'
FIRMWARE_URL='https://micropython.org/resources/firmware/esp8266-20210902-v1.17.bin'

if [[ $1 == /dev/ttyUSB* ]] ;then
    DEVICE="$1"
else
    DEVICE="/dev/ttyUSB$1"
fi

# download firmware
mkdir -p "/tmp"
if [ ! -e "/tmp/$FIRMWARE_NAME" ]; then
    wget $FIRMWARE_URL -O "/tmp/$FIRMWARE_NAME"
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
        esptool.py --port $DEVICE erase_flash
        esptool.py --port $DEVICE --baud 460800 write_flash --flash_size=detect 0 "/tmp/$FIRMWARE_NAME"
    fi
fi