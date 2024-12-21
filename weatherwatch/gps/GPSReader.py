import datetime
import pprint
import time

import adafruit_gps
import serial
from conf.AppConfig import AppConfig
from conf.GPSConfig import GPSConfig
from gps.GPSData import GPSData
from py_singleton import singleton
from util.Logger import logger

__all__ = ["GPSReader"]


@logger
@singleton
class GPSReader:
    """
    gps reader for lon lat alt
    https://github.com/adafruit/Adafruit_CircuitPython_GPS
    https://cdn.sparkfun.com/assets/parts/1/2/2/8/0/PMTK_Packet_User_Manual.pdf
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._gpsConfig: GPSConfig = AppConfig().gps

    def read(self) -> GPSData:
        """
        read gps data from receiver
        :param self: this
        """
        uart: serial.Seria = serial.Serial(self._gpsConfig.serial_device, baudrate=self._gpsConfig.baud_rate, timeout=1)
        try:
            gps: adafruit_gps.GPS = adafruit_gps.GPS(uart, debug=False)

            # PMTK_API_SET_NMEA_OUTPUT
            gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

            # PMTK_SET_NMEA_UPDATERATE
            gps.send_command(b"PMTK220,1000")
            time.sleep(1)
            gps.update()

            start = datetime.datetime.now()
            duration = 0
            while not gps.has_fix and duration < self._gpsConfig.init_timeout:
                time.sleep(0.5)
                gps.update()
                duration = self.duration(start)
                self.logger.debug("waiting on GPS %s", duration)

            if not gps.has_fix:
                raise IOError("initialize gps timeout")

            time.sleep(0.5)

            self.logger.debug(f"GPS {pprint.pformat(gps.__dict__)}")

            return GPSData(latitude=gps.latitude, longitude=gps.longitude, altitude=gps.altitude_m)
        finally:
            uart.close()

    def duration(self, start: datetime) -> int:
        """
        calculate the execution duration from start to now
        :param start: the processing start time
        """
        current = datetime.datetime.now()
        return int((current - start).total_seconds())
