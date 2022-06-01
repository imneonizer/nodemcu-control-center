import machine
from time import sleep

class RGBLed:
    def __init__(self, addr, i2c):
        self.addr = addr
        self.i2c = i2c
        self._write = lambda msg: self.i2c.writeto(
            self.addr, ('2'+msg).encode()
        )

        # aux methods
        self.on = lambda: self._write('111')
        self.off = lambda: self._write('000')
        self.rgb = lambda rgb: self._write(rgb)

        # rgb colors
        self.red = lambda: self._write('100')
        self.green = lambda: self._write('010')
        self.blue = lambda: self._write('001')

        # cmyk colors
        self.cyan = lambda: self._write('011')
        self.magenta = lambda: self._write('101')
        self.yellow = lambda: self._write('110')
    
    def blink(self, n=1, s=0.1, start_off=True, stop_off=True):
        # blink onboard led based on given paremeters
        self.yellow() if stop_off else self.off()
        for i in range(n):
            if start_off:
                self.off(); sleep(s); self.yellow()
            else:
                self.yellow(); sleep(s); self.off()
            if i <= n: sleep(s)
        self.yellow() if stop_off else self.off()


class ArduinoI2C:
    def __init__(self, sda_pin=5, scl_pin=4, arduino_addr=8, water_sensor_calibrate=1102):
        # Create an I2C object out of our SDA and SCL pin objects
        self.i2c = machine.I2C(
            sda=machine.Pin(sda_pin),
            scl=machine.Pin(scl_pin)
        )

        # I2C address of arduino attached to nodemcu
        self.arduino_addr = arduino_addr or self.i2c.scan()[0]
        self.water_sensor = machine.ADC(0)
        self.led = RGBLed(self.arduino_addr, self.i2c)
        self.water_sensor_calibrate = water_sensor_calibrate

    def read(self, num_bytes, addr=None):
        return self.i2c.readfrom((addr or self.arduino_addr), num_bytes).decode()

    def write(self, msg, addr=None):
        return self.i2c.writeto((addr or self.arduino_addr), msg.encode())

    def cast_to_int(self, data):
        try:
            return int(data)
        except:
            return -1

    def get_states(self):
        # 0|1 -> relay switch 1
        # 0|1 -> relay switch 2
        # 0|1 -> relay switch 3
        # 0|1 -> relay switch 4
        # 0|1 -> if 1 then water switch has been turned off by arduino
        # 0|1 -> if 1 then pir switch has been turned off by arduino
        return [self.cast_to_int(x) for x in self.read(6)]

    def read_water_sensor(self):
        prefix = ''
        reading = self.water_sensor.read()

        # caliberate value, due to different type of sensor
        reading = abs(reading - self.water_sensor_calibrate)

        if reading < 10:
            prefix = '00'
        elif reading < 100:
            prefix = '0'
        return (prefix+str(reading))[:3]

    def set_states(self, data):
        # data => [r1, r2, r3, r4]; 0/1 values
        # calibrate values, due to error in arduino
        data[-1] = int(not data[-1])
        return self.write('1' + ''.join([str(x) for x in data]) + self.read_water_sensor())
