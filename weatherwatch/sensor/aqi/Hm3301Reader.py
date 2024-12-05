#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
AQI sensor
https://wiki.seeedstudio.com/Grove-Laser_PM2.5_Sensor-HM3301/
code is mostly ccp from https://github.com/Seeed-Studio/grove.py
https://github.com/Seeed-Studio/grove.py/blob/master/grove/grove_PM2_5_HM3301.py
TODO sensor still is wanky
getting lots of crc fail and data that goes out of range
currently doing multiple reading to get something that seems valid

Please set the I2c speed to 20khz
    sudo vim /boot/config.txt
    dtparam=i2c_arm_baudrate=20000
    sudo reboot
"""

import time

from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig
from py_singleton import singleton
from sensor.aqi.Hm3301Data import Hm3301Data
from util.Logger import logger

import board
import busio
from adafruit_pm25.i2c import PM25_I2C


__all__ = ["Hm3301Reader"]


@logger
@singleton
class Hm3301Reader:

    HM3301_DEFAULT_I2C_ADDR = 0x40
    SELECT_I2C_ADDR = 0x88
    DATA_CNT = 29
    SM_BUS = 1

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._aqiConfig: AQIConfig = AppConfig().aqi

    def read(self) -> Hm3301Data:

        reset_pin = None
        i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        pm25 = PM25_I2C(i2c, reset_pin, address=Hm3301Reader.HM3301_DEFAULT_I2C_ADDR)

        time.sleep(1)

        aqdata = pm25.read()

        data = Hm3301Data()

        data.pm_1_0_conctrt_std = aqdata["pm10 standard"]
        data.pm_2_5_conctrt_std = aqdata["pm25 standard"]
        data.pm_10_conctrt_std = aqdata["pm100 standard"]

        data.pm_1_0_conctrt_atmosph = aqdata["pm10 env"]
        data.pm_2_5_conctrt_atmosph = aqdata["pm25 env"]
        data.pm_10_conctrt_atmosph = aqdata["pm100 env"]

        return data