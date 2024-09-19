import logging

from sensor.sdr import BaseData, IndoorData


class OutdoorData(IndoorData):
    RAIN_KEY = "rain_mm"
    WIND_AVE_KEY = "wind_avg_m_s"
    WIND_MAX_KEY = "wind_max_m_s"
    WIND_DIR_KEY = "wind_dir_deg"
    LUX_KEY = "light_lux"
    UV_KEY = "uv"

    """
    outdoor sensor data 
    """

    def __init__(
        self,
        timeStamp=None,
        id=None,
        model=None,
        channel=None,
        batteryOK=False,
        mic=None,
        mod=None,
        freq=None,
        rssi=None,
        noise=None,
        snr=None,
        temprature=None,
        humidity=None,
        rain_mm=None,
        wind_avg_m_s=None,
        wind_max_m_s=None,
        wind_dir_deg=None,
        light_lux=None,
        uv=None,
    ):
        """
        ctor
        :param self: this
        """
        super().__init__()
        self.timeStamp = timeStamp
        self.id = id
        self.model = model
        self.channel = channel
        self.batteryOk = batteryOK
        self.mic = mic
        self.mod = mod
        self.freq = freq
        self.rssi = rssi
        self.noise = noise
        self.snr = snr
        self.temperature = temprature
        self.humidity = humidity
        self.rain_mm = rain_mm
        self.wind_avg_m_s = wind_avg_m_s
        self.wind_max_m_s = wind_max_m_s
        self.wind_dir_deg = wind_dir_deg
        self.light_lux = light_lux
        self.uv = uv

    @staticmethod
    def jsonDecoder(d: dict) -> "OutdoorData":
        try:
            data = OutdoorData()
            BaseData.baseDecoder(data, d)
            data.temperature = d[IndoorData.TEMP_KEY]
            data.humidity = d[IndoorData.HUMID_KEY]
            data.rain_mm = d[OutdoorData.RAIN_KEY]
            data.wind_avg_m_s = d[OutdoorData.WIND_AVE_KEY]
            data.wind_max_m_s = d[OutdoorData.WIND_MAX_KEY]
            data.wind_dir_deg = d[OutdoorData.WIND_DIR_KEY]
            data.light_lux = d[OutdoorData.LUX_KEY]
            data.uv = d[OutdoorData.UV_KEY]
            return data
        except Exception as e:
            logging.error("failed to parse " + str(d) + "\n" + str(e))
            raise Exception("failed to parse " + str(d)) from e

    @property
    def rain_mm(self):
        """
        rain_mm string property getter
        :param self: this
        :return: the rain_mm
        """
        return self._rain_mm

    @rain_mm.setter
    def rain_mm(self, rain_mm):
        """
        rain_mm property setter
        :param self: this
        :param: the rain_mm
        """
        self._rain_mm = rain_mm

    @property
    def wind_dir_deg(self):
        """
        wind_dir_deg string property getter
        :param self: this
        :return: the wind_dir_deg
        """
        return self._wind_dir_deg

    @wind_dir_deg.setter
    def wind_dir_deg(self, wind_dir_deg):
        """
        wind_dir_deg property setter
        :param self: this
        :param: the wind_dir_deg
        """
        self._wind_dir_deg = wind_dir_deg

    @property
    def wind_avg_m_s(self):
        """
        wind_avg_m_s string property getter
        :param self: this
        :return: the wind_avg_m_s
        """
        return self._wind_avg_m_s

    @wind_avg_m_s.setter
    def wind_avg_m_s(self, wind_avg_m_s):
        """
        wind_avg_m_s property setter
        :param self: this
        :param: the wind_avg_m_s
        """
        self._wind_avg_m_s = wind_avg_m_s

    @property
    def wind_max_m_s(self):
        """
        wind_max_m_s string property getter
        :param self: this
        :return: the wind_max_m_s
        """
        return self._wind_max_m_s

    @wind_max_m_s.setter
    def wind_max_m_s(self, wind_max_m_s):
        """
        wind_max_m_s property setter
        :param self: this
        :param: the wind_max_m_s
        """
        self._wind_max_m_s = wind_max_m_s

    @property
    def light_lux(self):
        """
        light_lux string property getter
        :param self: this
        :return: the light_lux
        """
        return self._light_lux

    @light_lux.setter
    def light_lux(self, light_lux):
        """
        light_lux property setter
        :param self: this
        :param: the light_lux
        """
        self._light_lux = light_lux

    @property
    def uv(self):
        """
        uv string property getter
        :param self: this
        :return: the uv
        """
        return self._uv

    @uv.setter
    def uv(self, uv):
        """
        uv property setter
        :param self: this
        :param: the uv
        """
        self._uv = uv
