import json
from datetime import datetime

from conf.SensorConfig import SensorConfig
from util.Logger import logger

__all__ = ["BaseData"]


@logger
class BaseData:

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

    """
    base sensor data
    """

    def __init__(
        self,
        timeStamp=None,
        id=None,
        model=None,
        batteryOK=False,
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
        self.timeStamp = timeStamp
        self.model = model
        self.id = id
        self.batteryOk = batteryOK
        self.mic = mic
        self.mod = mod
        self.freq = freq
        self.rssi = rssi
        self.noise = noise
        self.snr = snr
        self.raw = raw
        self.config = config

    @staticmethod
    def baseDecoder(o: "BaseData", d: dict):
        try:
            o.timeStamp = datetime.strptime(d["time"], BaseData.DATE_FORMAT)
            o.model = d[BaseData.MODEL_KEY]
            o.id = int(d[BaseData.ID_KEY])
            o.batteryOk = d[BaseData.BATTERY_KEY] == 1
            o.mic = d[BaseData.MIC_KEY]
            o.mod = d[BaseData.MOD_KEY]
            o.freq = d[BaseData.FREQ_KEY]
            o.rssi = d[BaseData.RSSI_KEY]
            o.noise = d[BaseData.NOISE_KEY]
            o.snr = d[BaseData.SNR_KEY]
        except Exception as e:
            raise Exception(
                f"failed to parse {d}",
            ) from e

    @staticmethod
    def key(j):
        """
        key property getter
        :param self: this
        :return: the key
        """
        key = "[" + j[BaseData.MODEL_KEY] + "|" + str(j[BaseData.ID_KEY])

        if BaseData.CHANNEL_KEY in j:
            key = key + "|" + str(j[BaseData.CHANNEL_KEY])

        return key + "]"

    @property
    def timeStamp(self) -> datetime:
        """
        timestamp property getter
        :param self: this
        :return: the timestamp
        """
        return self._timeStamp

    @timeStamp.setter
    def timeStamp(self, timeStamp: datetime):
        """
        timeStamp property setter
        :param self: this
        :param: the timeStamp
        """
        self._timeStamp = timeStamp

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
    def id(self) -> int:
        """
        id property getter
        :param self: this
        :return: the id
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """
        id property setter
        :param self: this
        :param: the id
        """
        self._id = id

    @property
    def batteryOk(self) -> bool:
        """
        batteryOk property getter
        :param self: this
        :return: the batteryOk
        """
        return self._batteryOk

    @batteryOk.setter
    def batteryOk(self, batteryOk: bool):
        """
        batteryOk property setter
        :param self: this
        :param: the batteryOk
        """
        self._batteryOk = batteryOk

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
