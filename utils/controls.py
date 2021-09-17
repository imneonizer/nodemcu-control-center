import time

class Controls:
    def __init__(self, switches, expire=10):
        self.switches = switches
        self.states = {"-1":"Unknown", "0":"OFF", "1":"ON"}
        self.expire = expire
        self.init()
    
    def init(self):
        self.st = time.time()
        self.synced = False
        self.user_state = {k:"-1" for k in self.switches}
        self.mcu_state = {k:"-1" for k in self.switches}
    
    @property
    def is_synced(self):
        if time.time() - self.st > self.expire:
            self.init()
        return self.synced