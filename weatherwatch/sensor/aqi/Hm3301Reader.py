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
from smbus2 import SMBus, i2c_msg
from util.Logger import logger

__all__ = ["Hm3301Reader"]


@logger
@singleton
class Hm3301Reader:
    """
    aqi sensor reader
    using seeedstudio grove lib
    https://github.com/Seeed-Studio/grove.py/blob/master/grove/grove_PM2_5_HM3301.py
    """

    HM3301_DEFAULT_I2C_ADDR = 0x40
    SELECT_I2C_ADDR = 0x88
    DATA_CNT = 29
    SM_BUS = 1

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._aqi_config: AQIConfig = AppConfig().aqi

    def read(self) -> Hm3301Data:
        """
        read AQI sensor data
        :param self: this
        """

        data: Hm3301Data = None
        cnt: int = 0
        while cnt < self._aqi_config.retry and data is None:

            # TODO what's the arg for
            with SMBus(Hm3301Reader.SM_BUS) as bus:
                write = i2c_msg.write(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, [Hm3301Reader.SELECT_I2C_ADDR])
                bus.i2c_rdwr(write)

            time.sleep(self._aqi_config.wait_sec)

            with SMBus(Hm3301Reader.SM_BUS) as bus:
                read = i2c_msg.read(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, Hm3301Reader.DATA_CNT)
                bus.i2c_rdwr(read)
                raw = list(read)

            crc_checksum = 0
            for i in range(Hm3301Reader.DATA_CNT - 1):
                crc_checksum += raw[i]
            crc_checksum = crc_checksum & 0xFF

            if crc_checksum == raw[28]:
                data = Hm3301Data()

                data.pm_1_0_conctrt_std = raw[4] << 8 | raw[5]
                data.pm_2_5_conctrt_std = raw[6] << 8 | raw[7]
                data.pm_10_conctrt_std = raw[8] << 8 | raw[9]

                data.pm_1_0_conctrt_atmosph = raw[10] << 8 | raw[11]
                data.pm_2_5_conctrt_atmosph = raw[12] << 8 | raw[13]
                data.pm_10_conctrt_atmosph = raw[14] << 8 | raw[15]

            else:
                self.logger.warning("HM3301 crc checksum failed")

        if data is None:
            raise ValueError("retry exceeded")

        return data
