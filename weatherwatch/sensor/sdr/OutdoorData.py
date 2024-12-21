from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData

__all__ = ["OutdoorData"]


class OutdoorData(IndoorData):
    """
    outdoor sensor data
    """

    RAIN_KEY = "rain_mm"
    WIND_AVE_KEY = "wind_avg_m_s"
    WIND_MAX_KEY = "wind_max_m_s"
    WIND_DIR_KEY = "wind_dir_deg"
    LUX_KEY = "light_lux"
    UV_KEY = "uv"

    def __init__(
        self,
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
        self.rain_mm = rain_mm
        self.wind_avg_m_s = wind_avg_m_s
        self.wind_max_m_s = wind_max_m_s
        self.wind_dir_deg = wind_dir_deg
        self.light_lux = light_lux
        self.uv = uv
        super().__init__()

    @staticmethod
    def json_decoder(raw: dict) -> "OutdoorData":
        """
        json data decoder
        :param raw: raw dictionary data
        """
        try:
            data = OutdoorData()
            BaseData.base_decoder(data, raw)
            data.temperature = raw[IndoorData.TEMP_KEY]
            data.humidity = raw[IndoorData.HUMID_KEY]
            data.rain_mm = raw[OutdoorData.RAIN_KEY]
            data.wind_avg_m_s = raw[OutdoorData.WIND_AVE_KEY]
            data.wind_max_m_s = raw[OutdoorData.WIND_MAX_KEY]
            data.wind_dir_deg = raw[OutdoorData.WIND_DIR_KEY]
            data.light_lux = raw[OutdoorData.LUX_KEY]
            data.uv = raw[OutdoorData.UV_KEY]
            return data
        except Exception as e:
            raise Exception("failed to parse " + str(raw)) from e

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
