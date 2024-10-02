__all__ = ["BMPData"]


class BMPData:
    """
    bp388 sensor data
    """

    def __init__(self, temperature=None, pressure=None, altitude=None):
        self._temperature = temperature
        self._pressure = pressure
        self._altitude = altitude

    # override
    def __str__(self):
        return str(self.__dict__)

    @property
    def temperature(self):
        """
        temperature string property getter
        :param self: this
        :return: the temperature
        """
        return self._temperature

    @temperature.setter
    def temperature(self, temperature):
        """
        temperature property setter
        :param self: this
        :param: the temperature
        """
        self._temperature = temperature

    @property
    def pressure(self):
        """
        pressure string property getter
        :param self: this
        :return: the pressure
        """
        return self._pressure

    @pressure.setter
    def pressure(self, pressure):
        """
        pressure property setter
        :param self: this
        :param: the pressure
        """
        self._pressure = pressure

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
