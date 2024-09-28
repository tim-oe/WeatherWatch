import adafruit_bmp3xx
import board

from src.sensor.bmp.BMPData import BMPData

__all__ = ["Bmp388SensorReader"]


class Bmp388SensorReader(object):
    """
    adafruit bmp388 sensor reader
    lib: https://github.com/adafruit/Adafruit_CircuitPython_BMP3XX
    circuitPyton: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    sensor: https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx
    doc: https://docs.circuitpython.org/projects/bmp3xx/en/latest/
    """

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Bmp388SensorReader, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        #
        # I2C setup
        self.i2c = board.I2C()  # uses board.SCL and board.SDA

        self.bmp = adafruit_bmp3xx.BMP3XX_I2C(self.i2c)

        # TODO what are these for, from sample
        self.bmp.pressure_oversampling = 8
        self.bmp.temperature_oversampling = 2

    def read(self) -> BMPData:
        """
        read sensor data
        """
        return BMPData(
            pressure=self.bmp.pressure,
            temperature=self.bmp.temperature,
            altitude=self.bmp.altitude,
        )
