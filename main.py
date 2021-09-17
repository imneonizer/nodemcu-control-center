from machine import Pin
from time import sleep
import network
import esp
import gc
esp.osdebug(None)

SSID = "OnePlus 8"
PASSWORD = "123456789009"
AUTH_TOKEN = "9557fd34-fd86-401a-8f32-02b22fad2c1c"
SERVER = "http://192.168.204.131:5000/"

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

connect_wifi(SSID, PASSWORD)

try:
    import urequests as requests
except:
    import upip
    upip.install("micropython-urequests")
    import urequests as requests

gc.collect()

pins = dict(
    D0 = Pin(16, Pin.OUT),
    D1 = Pin(5, Pin.OUT),
    D2 = Pin(4, Pin.OUT),
    D3 = Pin(2, Pin.OUT),
    D5 = Pin(14, Pin.OUT),
    D6 = Pin(12, Pin.OUT),
    D7 = Pin(13, Pin.OUT)
)

while True:
    try:
        # get state change request from the server
        r = requests.get(SERVER+"/mcu-get-update").json()
        print("-"*10)
        for (name, value_to_set) in r.items():
            p = pins.get(name, None)
            if not p: continue
            
            if str(value_to_set) == "0":
                # it's a bug mcu return opposite values
                # hence p.on() means setting it to off
                p.on()
            elif str(value_to_set) == "1":
                p.off()
            
            # print live pin values
            print(name, str(int(not bool(p.value()))))
        
        # send latest update to the server
        state = '&'.join([n+"="+str(int(not bool(p.value()))) for (n,p) in pins.items()])
        r = requests.get(SERVER+"/mcu-set-update?"+state)
        gc.collect()
    except Exception as e:
        print(e)
        gc.collect()
        connect_wifi(SSID, PASSWORD, check=True)

    sleep(0.5)