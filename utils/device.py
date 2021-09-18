import time
import json
import re

class ESPDevice:
    def __init__(self, labels, alias=None, expire=30):
        self.expire = expire
        self.alias = alias if alias else 'NodeMCU'
        self.labels = json.loads(labels)
        self.init()
    
    def init(self):
        self.st = time.time()
        self.synced = False
        self.user_state = {k:"unknown" for k in self.labels}
        self.mcu_state = {k:"unknown" for k in self.labels}
    
    @property
    def is_synced(self):
        if time.time() - self.st > self.expire:
            self.init()
        return self.synced
    
    def sync_state(self, data):
        self.mcu_state.update(data)
        # self.user_state.update(data)
        self.st = time.time()
        self.synced = True

    def get_labels(self):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda item: [convert(c) for c in re.split('([0-9]+)', item[0])]
        return sorted(self.labels.items(), key=alphanum_key)