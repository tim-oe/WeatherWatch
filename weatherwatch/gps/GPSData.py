from gps.DMSCoordinate import DMSCoordinate
from util.Logger import logger

__all__ = ["GPSData"]


@logger
class GPSData:
    """
    bp388 sensor data
    """

    def __init__(self, latitude=None, longitude=None, altitude=None):
        self._latitude = latitude
        self._longitude = longitude
        self._altitude = altitude

    @property
    def latitude(self):
        """
        latitude string property getter
        :param self: this
        :return: the latitude
        """
        return self._latitude

    @property
    def latitude_dms(self):
        """
        latitude dms property getter
        :param self: this
        :return: the latitude dms
        """
        return DMSCoordinate(self._latitude, True)

    @latitude.setter
    def latitude(self, latitude):
        """
        latitude property setter
        :param self: this
        :param: the latitude
        """
        self._latitude = latitude

    @property
    def longitude(self):
        """
        longitude string property getter
        :param self: this
        :return: the longitude
        """
        return self._longitude

    @property
    def longitude_dms(self):
        """
        longitude dms property getter
        :param self: this
        :return: the longitude dms
        """
        return DMSCoordinate(self._longitude, False)

    @longitude.setter
    def longitude(self, longitude):
        """
        longitude property setter
        :param self: this
        :param: the longitude
        """
        self._longitude = longitude

    @property
    def altitude(self):
        """
        altitude string property getter
        :param self: this
        :return: the altitude
        """
        return self._altitude

    @altitude.setter
    def altitude(self, altitude):
        """
        altitude property setter
        :param self: this
        :param: the altitude
        """
        self._altitude = altitude
