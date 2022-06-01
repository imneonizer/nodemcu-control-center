import mfrc522

class RFID:
    def __init__(self, sck=12, mosi=13, miso=15, rst=0, cs=14):
        self.rdr = mfrc522.MFRC522(
            sck=sck,
            mosi=mosi,
            miso=miso,
            rst=rst,
            cs=cs
        )
    
    def read(self):
        try:
            (status, tag_type) = self.rdr.request(self.rdr.REQIDL)
            if status == self.rdr.OK:
                (status, raw_uid) = self.rdr.anticoll()
                if status == self.rdr.OK:
                    if self.rdr.select_tag(raw_uid) == self.rdr.OK:
                        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                        if self.rdr.auth(self.rdr.AUTHENT1A, 8, key, raw_uid) == self.rdr.OK:
                            address = self.rdr.read(8)
                            self.rdr.stop_crypto1()
                            return address
                        else:
                            print("Authentication error")
                    else:
                        print("Failed to select tag")
        except Exception as e:
            print(e)
        return []