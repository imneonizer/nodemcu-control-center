# import statements
from machine import Pin
from time import sleep
import network
import ubinascii
import esp
import ujson as json
import gc
esp.osdebug(None)

############ Credentials ################
SSID = "OnePlus 8"
PASSWORD = "123456789009"
# SERVER = "http://192.168.204.131:5000"
SERVER = "https://mcu-control.herokuapp.com/"
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

pins = {
    "D0": Pin(16, Pin.OUT),
    "D1": Pin(5, Pin.OUT),
    "D2": Pin(4, Pin.OUT),
    "D3": Pin(0, Pin.OUT),
    "D4": Pin(2, Pin.OUT),
    "D5": Pin(14, Pin.OUT),
    "D6": Pin(12, Pin.OUT),
    "D7": Pin(13, Pin.OUT),
    "D8": Pin(15, Pin.OUT)
}

headers = {
    'content-type': 'application/json',
    'auth_token': AUTH_TOKEN,
    'device_id': ubinascii.hexlify(network.WLAN().config('mac'),':').decode(),
    'alias': "Office Area",
    'labels':  json.dumps({
        "D0":"Switch 0",
        "D1":"Switch 1",
        "D2":"Switch 2",
        "D3":"Switch 3",
        "D4":"Onboard Led",
        "D5":"Switch 5",
        "D6":"Switch 6",
        "D7":"Switch 7",
        "D8":"Switch 8"
    })
}

def parse_value(p):
    return "on" if bool(p.value()) else "off"

gc.collect()

# Event loop
while True:
    try:
        # get state change request from the server
        r = requests.get(SERVER+"/mcu-get-update", headers=headers)
        if r.status_code != 200: sleep(0.5); continue
        r = r.json()
    
        print("-"*10)
        for (name, value_to_set) in r.items():
            p = pins.get(name, None)
            if not p: continue

            if value_to_set == "off":
                p.off()
            elif value_to_set == "on":
                p.on()

            # print live pin values
            print(name, "=", parse_value(p))

        # send latest update to the server
        state = json.dumps({k:parse_value(p) for (k,p) in pins.items()})
        r = requests.post(SERVER+"/mcu-set-update", headers=headers, data=state)
        gc.collect()
    except Exception as e:
        print(e)
        gc.collect()
        connect_wifi(SSID, PASSWORD, check=True)
    sleep(0.1)