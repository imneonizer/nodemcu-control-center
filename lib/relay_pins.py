import time
try:
    # try to import urequests
    import urequests as requests
except:
    # if not found install via upip
    import upip
    upip.install("micropython-urequests")
    import urequests as requests

class RelayPins:
    def __init__(self, aic):
        self.aic = aic
        self.pins = {
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'R4': 0
        }
        
        self.water_tank_full_notif_st = time.time()
        self.gate_closed_notif_st = time.time()
        self.msg_interval = 1

    def send(self):
        r = self.aic.get_states()
        if r[4] == 1:
            if time.time() - self.water_tank_full_notif_st > self.msg_interval:
                self.water_tank_full_notif_st = time.time()
                print("[{}] water pump turned off!".format(time.time()))
                requests.get("https://maker.ifttt.com/trigger/water_pump_off/json/with/key/cui6sM6wOD_M0aN-QhHxXMWqslZlKzPWWbfZ8hg8QLx")
        if r[5] == 1:
            if (time.time() - self.gate_closed_notif_st > self.msg_interval):
                self.gate_closed_notif_st = time.time()
                print("[{}] gate closed!".format(time.time()))
                requests.get("https://maker.ifttt.com/trigger/gate_closed/json/with/key/cui6sM6wOD_M0aN-QhHxXMWqslZlKzPWWbfZ8hg8QLx")
                
        
        return self.aic.set_states([
            self.pins.get('R1'),
            self.pins.get('R2'),
            self.pins.get('R3'),
            self.pins.get('R4'),
        ])
    
    def receive(self):
        r = self.aic.get_states()
        self.pins.update({
            "R1": r[0],
            "R2": r[1],
            "R3": r[2],
            "R4": r[3]
        })
        
        return r

    def read(self, pin):
        return self.parses_value(self.pins.get(pin.upper(), None))

    def on(self, pin):
        self.pins.update({pin.upper(): 1})
        self.send()

    def off(self, pin):
        self.pins.update({pin.upper(): 0})
        self.send()

    def exist(self, name):
        if name.upper() in self.pins:
            return name

    def parses_value(self, pin):
        return 'on' if bool(pin) else 'off'

    def items(self):        
        return {
            'R1': self.parses_value(self.pins.get('R1')),
            'R2': self.parses_value(self.pins.get('R2')),
            'R3': self.parses_value(self.pins.get('R3')),
            'R4': self.parses_value(self.pins.get('R4'))
        }