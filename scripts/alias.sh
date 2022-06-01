#! /bin/bash
# script to work with esp8266 based nodemcu


if [[ $1 == /dev/ttyUSB* ]] ;then
    DEVICE="$1"
else
    DEVICE="/dev/ttyUSB$1"
fi

# check if script is being sourced
if [[ ! "${BASH_SOURCE[0]}" != "${0}" ]];then
    echo "Usage: source $0 $@"
    exit
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
        alias mcp='_(){ ampy put $1 $1; }; _'
        alias acp="ampy put"
        alias mpy="ampy run"
        alias deploy="ampy put lib; ampy put src; ampy put main.py"
    fi
fi