# import statements
from machine import Pin
from time import sleep
import network
import ubinascii
import esp
import ujson as json
import gc
from lib.arduino_i2c import ArduinoI2C
from lib.relay_pins import RelayPins
esp.osdebug(None)

############ Credentials ################
SSID = "imiot"
PASSWORD = "super_secret"
SERVER = "http://192.168.0.90:5000"
AUTH_TOKEN = "token"
#######################################s##


def connect_wifi(ssid, password, check=False):
    station = network.WLAN(network.STA_IF)
    if check and station.isconnected():
        return

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())


# connect to the wifi on boot
connect_wifi(SSID, PASSWORD)

try:
    # try to import urequests
    import urequests as requests
except:
    # if not found install via upip
    import upip
    upip.install("micropython-urequests")
    import urequests as requests

aic = ArduinoI2C()
pins = RelayPins(aic)

headers = {
    'content-type': 'application/json',
    'auth_token': AUTH_TOKEN,
    'device_id': ubinascii.hexlify(network.WLAN().config('mac'), ':').decode(),
    'alias': "Office Area",
    'labels':  json.dumps({
        "R1": "Water Pump",
        "R2": "Smart Gate",
        "R3": "Relay 3",
        "R4": "Relay 4",
    })
}

gc.collect()

# Event loop
while True:
    try:
        # get state change request from the server
        r = requests.get(SERVER+"/mcu-get-update", headers=headers)
        if r.status_code != 200:
            sleep(0.5)
            continue

        r = r.json()

        # print("-"*10)
        for (name, value_to_set) in r.items():
            p = pins.exist(name)
            if not p:
                continue

            if value_to_set == "off":
                pins.off(p)
            elif value_to_set == "on":
                pins.on(p)
            else:
                # update pin state via i2c
                pins.send()

            # print live pin values
            # print(name, "=", pins.read(p))

        # print("WS = %s" % aic.read_water_sensor())
        # send latest update to the server
        state = json.dumps(pins.items())
        r = requests.post(SERVER+"/mcu-set-update",
                          headers=headers, data=state)
        gc.collect()
    except Exception as e:
        print(e)
        gc.collect()
        connect_wifi(SSID, PASSWORD, check=True)
    sleep(0.3)
