# import statements
from machine import Pin
import time
from time import sleep
import network
import ubinascii
import esp
import ujson as json
import gc
from lib.arduino_i2c import ArduinoI2C
from lib.relay_pins import RelayPins
# from lib.rfid import RFID
esp.osdebug(None)

############ Credentials ################
SSID = "imiot"
PASSWORD = "super_secret"
SERVER = "http://192.168.0.90:5000"
SERVER="http://flaskiot.duckdns.org"
AUTH_TOKEN = "token"
#######################################s##

ap = network.WLAN(network.AP_IF)
ap.active(False)

aic = ArduinoI2C()
pins = RelayPins(aic)
# rfid = RFID()

def connect_wifi(ssid, password, check=False):
    aic.led.yellow()
    print("connecting to wifi... {}".format(SSID))
    station = network.WLAN(network.STA_IF)
    if check and station.isconnected():
        return

    station.active(True)
    station.connect(ssid, password)

    while station.isconnected() == False:
        pass

    print('Connection successful')
    print(station.ifconfig())
    aic.led.off()


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

# known_rfid_address = {
#     'card': [92, 120, 51, 48, 92, 120, 51, 48, 92, 120, 51, 48, 92, 120, 51, 48],
# }

gc.collect()
# rfid_st = time.time()
aic.led.off()

def main():
    print
    # Event loop
    while True:
        try:        
            # handle rfid read
            # if (time.time() - rfid_st > 1.5):
            #     rfid_st = time.time()
            #     address = rfid.read()
            #     if not address:
            #         pass
            #     elif address in known_rfid_address.values():
            #         # open the gate as rfid address matches
            #         pins.on("R2")
            #         aic.led.green()
            #     else:
            #         aic.led.red()
                    

            # get state change request from the server
            r = requests.get(SERVER+"/mcu-get-update", headers=headers)
            if r.status_code != 200:
                sleep(0.03)
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
            aic.led.red()
            print(e)
            gc.collect()
            connect_wifi(SSID, PASSWORD, check=True)
        sleep(0.2)

main()