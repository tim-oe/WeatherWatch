import time

import adafruit_tsl2591
import board
from adafruit_tsl2591 import TSL2591
from py_singleton import singleton
from sensor.light.Tsl2591Data import Tsl2591Data

__all__ = ["Tsl2591SensorReader"]


@singleton
class Tsl2591SensorReader:
    """
    adafruit tsl2591 sensor reader
    lib: https://github.com/adafruit/Adafruit_CircuitPython_TSL2591
    circuitPyton: https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
    sensor: https://learn.adafruit.com/adafruit-tsl2591-light-sensor
    github: https://github.com/adafruit/Adafruit_CircuitPython_TSL2591
    doc: https://docs.circuitpython.org/projects/tsl2591/en/latest/
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.tsl2591 = TSL2591(self.i2c)

    def read(self):  # -> Tsl2591Data:
        """
        read sensor data
        """
        try:
            lux: float = self.tsl2591.lux
        except Exception as e:
            self.logger.exception("failed to read lux")
            self.tsl2591.gain = adafruit_tsl2591.GAIN_LOW
            time.sleep(0.2)

        return Tsl2591Data(
            lux=self.tsl2591.lux,
            visible=self.tsl2591.visible,
            infrared=self.tsl2591.infrared,
            full_spectrum=self.tsl2591.full_spectrum,
            raw_luminosity=self.tsl2591.raw_luminosity,
        )

    def get_lux(self) -> float:
        """
        read lux, with sensor gain auto-switching to avoid saturation or underflow.
        :param tsl: the tsl2591 sensor
        :return: the lux
        """
        try:
            lux: float = self.tsl2591.lux
        except Exception as e:
            self.logger.exception("failed to read lux")
            self.tsl2591.gain = adafruit_tsl2591.GAIN_LOW
            time.sleep(0.2)
            lux = self.tsl2591.lux

        # If sensor is saturated (raw counts maxed), switch to lower gain
        if self.tsl2591.full_spectrum >= 37000 and self.tsl2591.gain != adafruit_tsl2591.GAIN_LOW:
            self.tsl2591.gain = adafruit_tsl2591.GAIN_LOW
            time.sleep(0.2)
            lux = self.tsl2591.lux
        # If sensor is too dark for low gain, switch to higher gain
        elif self.tsl2591.full_spectrum < 100 and self.tsl2591.gain == adafruit_tsl2591.GAIN_LOW:
            self.tsl2591.gain = adafruit_tsl2591.GAIN_MED
            time.sleep(0.2)
            lux = self.tsl2591.lux

        return round(max(lux, 0.001), 4)  # floor to avoid log(0)
