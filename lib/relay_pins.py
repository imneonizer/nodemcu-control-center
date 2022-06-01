class RelayPins:
    def __init__(self, aic):
        self.aic = aic
        self.pins = {
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'R4': 0
        }

    def send(self):
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
        
        if r[4] == 1:
            print("water pump turned off!")
        
        if r[5] == 1:
            print("pir switch turned off!")

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