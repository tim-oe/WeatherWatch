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

Please set the I2c speed to 20khz
    sudo vim /boot/config.txt
    dtparam=i2c_arm_baudrate=20000
    sudo reboot
"""


from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig
from py_singleton import singleton
from sensor.aqi.Hm3301Data import Hm3301Data
from smbus2 import SMBus, i2c_msg

__all__ = ["Hm3301Reader"]


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

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self._aqiConfig.enable

    def read(self) -> Hm3301Data:
        # TODO what's the arg
        with SMBus(Hm3301Reader.SM_BUS) as bus:
            write = i2c_msg.write(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, [Hm3301Reader.SELECT_I2C_ADDR])
            bus.i2c_rdwr(write)

        with SMBus(Hm3301Reader.SM_BUS) as bus:
            read = i2c_msg.read(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, Hm3301Reader.DATA_CNT)
            bus.i2c_rdwr(read)
            raw = list(read)

        sum = 0
        for i in range(Hm3301Reader.DATA_CNT - 1):
            sum += raw[i]
        sum = sum & 0xFF

        if sum == raw[28]:
            data: Hm3301Data = Hm3301Data()

            data.pm_1_0_conctrt_std = raw[4] << 8 | raw[5]
            data.pm_2_5_conctrt_std = raw[6] << 8 | raw[7]
            data.pm_10_conctrt_std = raw[8] << 8 | raw[9]

            data.pm_1_0_conctrt_atmosph = raw[10] << 8 | raw[11]
            data.pm_2_5_conctrt_atmosph = raw[12] << 8 | raw[13]
            data.pm_10_conctrt_atmosph = raw[14] << 8 | raw[15]

            return data
        else:
            raise ValueError("HM3301 crc check failed")
