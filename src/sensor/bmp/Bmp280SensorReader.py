import board
import adafruit_bmp280

from src.sensor.bmp.SensorData import SensorData

class Bmp280SensorReader(object):
    """
    seeedstudio bmp280 sensor reader
    TODO: _CHIP_ID = const(0x60)
    lib: https://github.com/adafruit/Adafruit_CircuitPython_BMP280
    circuitPyton: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    sensor: https://www.seeedstudio.com/Grove-Barometer-Sensor-BMP280.html
    doc: https://docs.circuitpython.org/projects/bmp280/en/latest/
    """

    def __init__(self):
        #
        # I2C setup
        self.i2c = board.I2C()  # uses board.SCL and board.SDA

        self.bmp = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c, 0x76)

        # TODO what are these for, from sample
        self.bmp.pressure_oversampling = 8
        self.bmp.temperature_oversampling = 2

    def read(self) -> SensorData:
        """
        read sensor data
        """
        return SensorData(
            pressure=self.bmp.pressure,
            temperature=self.bmp.temperature,
            altitude=self.bmp.altitude,
        )