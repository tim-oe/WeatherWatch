import json
from datetime import datetime
from typing import Self

from conf.SensorConfig import SensorConfig
from util.Logger import logger

__all__ = ["BaseData"]


@logger
class BaseData:
    """
    base sensor data
    """

    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIME_KEY = "time"
    MODEL_KEY = "model"
    ID_KEY = "id"
    # used by indoor sensor
    CHANNEL_KEY = "channel"
    BATTERY_KEY = "battery_ok"
    MIC_KEY = "mic"
    MOD_KEY = "mod"
    FREQ_KEY = "freq"
    RSSI_KEY = "rssi"
    NOISE_KEY = "noise"
    SNR_KEY = "snr"

    def __init__(
        self,
        time_stamp=None,
        sensor_id=None,
        model=None,
        battery_ok=False,
        mic=None,
        mod=None,
        freq=None,
        rssi=None,
        noise=None,
        snr=None,
        raw=None,
        config=None,
    ):
        """
        ctor
        :param self: this
        """
        self.time_stamp = time_stamp
        self.model = model
        self.sensor_id = sensor_id
        self.battery_ok = battery_ok
        self.mic = mic
        self.mod = mod
        self.freq = freq
        self.rssi = rssi
        self.noise = noise
        self.snr = snr
        self.raw = raw
        self.config = config

    @staticmethod
    def base_decoder(o: Self, raw: dict):
        """
        base data decoder
        :param o: the base data object
        :param raw: raw dictionary data
        """
        try:
            o.time_stamp = datetime.strptime(raw["time"], BaseData.DATE_FORMAT)
            o.model = raw[BaseData.MODEL_KEY]
            o.sensor_id = int(raw[BaseData.ID_KEY])
            o.battery_ok = raw[BaseData.BATTERY_KEY] == 1
            o.mic = raw[BaseData.MIC_KEY]
            o.mod = raw[BaseData.MOD_KEY]
            o.freq = raw[BaseData.FREQ_KEY]
            o.rssi = raw[BaseData.RSSI_KEY]
            o.noise = raw[BaseData.NOISE_KEY]
            o.snr = raw[BaseData.SNR_KEY]
        except Exception as e:
            raise Exception(
                f"failed to parse {raw}",
            ) from e

    @staticmethod
    def key(raw: dict) -> str:
        """
        generate sensor key from dictionary
        :param raw: the raw dictionary
        :return: the key
        """
        key = "[" + raw[BaseData.MODEL_KEY] + "|" + str(raw[BaseData.ID_KEY])

        if BaseData.CHANNEL_KEY in raw:
            key = key + "|" + str(raw[BaseData.CHANNEL_KEY])

        return key + "]"

    @property
    def time_stamp(self) -> datetime:
        """
        timestamp property getter
        :param self: this
        :return: the timestamp
        """
        return self._time_stamp

    @time_stamp.setter
    def time_stamp(self, time_stamp: datetime):
        """
        timeStamp property setter
        :param self: this
        :param: the timeStamp
        """
        self._time_stamp = time_stamp

    @property
    def model(self):
        """
        model property getter
        :param self: this
        :return: the model
        """
        return self._model

    @model.setter
    def model(self, model):
        """
        model property setter
        :param self: this
        :param: the model
        """
        self._model = model

    @property
    def sensor_id(self) -> int:
        """
        id property getter
        :param self: this
        :return: the id
        """
        return self._sensor_id

    @sensor_id.setter
    def sensor_id(self, sensor_id: int):
        """
        id property setter
        :param self: this
        :param: the id
        """
        self._sensor_id = sensor_id

    @property
    def battery_ok(self) -> bool:
        """
        batteryOk property getter
        :param self: this
        :return: the batteryOk
        """
        return self._battery_ok

    @battery_ok.setter
    def battery_ok(self, battery_ok: bool):
        """
        batteryOk property setter
        :param self: this
        :param: the batteryOk
        """
        self._battery_ok = battery_ok

    @property
    def mic(self):
        """
        mic property getter
        :param self: this
        :return: the mic
        """
        return self._mic

    @mic.setter
    def mic(self, mic):
        """
        mic property setter
        :param self: this
        :param: the mic
        """
        self._mic = mic

    @property
    def mod(self):
        """
        mod property getter
        :param self: this
        :return: the mod
        """
        return self._mod

    @mod.setter
    def mod(self, mod):
        """
        mod property setter
        :param self: this
        :param: the mod
        """
        self._mod = mod

    @property
    def freq(self):
        """
        freq property getter
        :param self: this
        :return: the freq
        """
        return self._freq

    @freq.setter
    def freq(self, freq):
        """
        freq property setter
        :param self: this
        :param: the freq
        """
        self._freq = freq

    @property
    def rssi(self):
        """
        rssi property getter
        :param self: this
        :return: the rssi
        """
        return self._rssi

    @rssi.setter
    def rssi(self, rssi):
        """
        rssi property setter
        :param self: this
        :param: the rssi
        """
        self._rssi = rssi

    @property
    def snr(self):
        """
        snr property getter
        :param self: this
        :return: the snr
        """
        return self._snr

    @snr.setter
    def snr(self, snr):
        """
        snr property setter
        :param self: this
        :param: the snr
        """
        self._snr = snr

    @property
    def noise(self):
        """
        noise property getter
        :param self: this
        :return: the noise
        """
        return self._noise

    @noise.setter
    def noise(self, noise):
        """
        noise property setter
        :param self: this
        :param: the noise
        """
        self._noise = noise

    @property
    def raw(self) -> json:
        """
        raw json property getter
        :param self: this
        :return: the raw
        """
        return self._raw

    @raw.setter
    def raw(self, raw):
        """
        raw json property setter
        :param self: this
        :param: the raw
        """
        self._raw = raw

    @property
    def config(self) -> SensorConfig:
        """
        config property getter
        :param self: this
        :return: the config
        """
        return self._config

    @config.setter
    def config(self, config):
        """
        config property setter
        :param self: this
        :param: the config
        """
        self._config = config
