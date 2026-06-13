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

The HM3301 is a notoriously finicky I2C device. Two things matter for
reliable, crc-clean reads:

1) I2C bus speed. Seeed explicitly require the bus be slowed to 20kHz.
   The default 100kHz/400kHz clock overruns the sensor and produces
   corrupt frames / crc failures. This is a system level setting:
       sudo vim /boot/config.txt
       dtparam=i2c_arm_baudrate=20000
       sudo reboot

2) Read sequencing. The 0x88 "select" byte is a one-time UART->I2C mode
   switch; the reference driver issues it once at startup and then simply
   reads 29 bytes per poll. Re-issuing select before every read (and
   re-opening the bus each time) adds bus churn while the sensor is mid
   measurement, which provokes more corrupt frames. We therefore warm the
   sensor up once and then retry the read on a short, sensor-cadence
   backoff (the device latches a fresh frame roughly once per second).
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
    # the sensor refreshes a frame roughly once per second, so a short
    # pause between failed attempts lets it latch a fresh, consistent frame
    # rather than re-reading the same half-updated buffer
    RETRY_WAIT_SEC = 1

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._aqi_config: AQIConfig = AppConfig().aqi
        # the 0x88 select / 30s power-on stabilization only needs to happen
        # once for the life of the process; tracked here so repeated reads
        # don't re-toggle the sensor mode on every poll
        self._warmed_up: bool = False

    def _warm_up(self, bus: SMBus):
        """
        switch the sensor to I2C output mode and let it stabilize.
        this is a one-time operation; the 0x88 select byte is a UART->I2C
        mode switch and the datasheet calls for ~30s of settle time after
        power-on before readings are trustworthy.
        :param self: this
        :param bus: an open smbus connection
        """
        if self._warmed_up:
            return

        write = i2c_msg.write(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, [Hm3301Reader.SELECT_I2C_ADDR])
        bus.i2c_rdwr(write)
        time.sleep(self._aqi_config.wait_sec)
        self._warmed_up = True

    @staticmethod
    def _crc_valid(raw: list) -> bool:
        """
        validate the trailing checksum byte against the sum of the frame
        :param raw: the 29 byte frame
        :return: True when the checksum matches
        """
        if len(raw) != Hm3301Reader.DATA_CNT:
            return False

        crc_checksum = 0
        for i in range(Hm3301Reader.DATA_CNT - 1):
            crc_checksum += raw[i]
        crc_checksum = crc_checksum & 0xFF

        return crc_checksum == raw[Hm3301Reader.DATA_CNT - 1]

    @staticmethod
    def _parse(raw: list) -> Hm3301Data:
        """
        parse a validated 29 byte frame into sensor data
        :param raw: the 29 byte frame
        :return: the parsed data
        """
        data = Hm3301Data()

        data.pm_1_0_conctrt_std = raw[4] << 8 | raw[5]
        data.pm_2_5_conctrt_std = raw[6] << 8 | raw[7]
        data.pm_10_conctrt_std = raw[8] << 8 | raw[9]

        data.pm_1_0_conctrt_atmosph = raw[10] << 8 | raw[11]
        data.pm_2_5_conctrt_atmosph = raw[12] << 8 | raw[13]
        data.pm_10_conctrt_atmosph = raw[14] << 8 | raw[15]

        return data

    def read(self) -> Hm3301Data:
        """
        read AQI sensor data
        :param self: this
        """

        data: Hm3301Data = None
        cnt: int = 0

        with SMBus(Hm3301Reader.SM_BUS) as bus:
            self._warm_up(bus)

            while cnt < self._aqi_config.retry and data is None:
                cnt += 1

                try:
                    read = i2c_msg.read(Hm3301Reader.HM3301_DEFAULT_I2C_ADDR, Hm3301Reader.DATA_CNT)
                    bus.i2c_rdwr(read)
                    raw = list(read)
                except OSError as ex:
                    self.logger.warning("HM3301 i2c read failed (attempt %d/%d): %s", cnt, self._aqi_config.retry, ex)
                    time.sleep(Hm3301Reader.RETRY_WAIT_SEC)
                    continue

                if not Hm3301Reader._crc_valid(raw):
                    self.logger.warning("HM3301 crc checksum failed (attempt %d/%d)", cnt, self._aqi_config.retry)
                    time.sleep(Hm3301Reader.RETRY_WAIT_SEC)
                    continue

                data = Hm3301Reader._parse(raw)

        if data is None:
            raise ValueError("retry exceeded")

        return data
