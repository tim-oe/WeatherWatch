from util.Logger import logger

__all__ = ["SensorConfig"]


# members are set dynamically
# pylint: disable=no-member
@logger
class SensorConfig:
    """
    sensor config data
    """

    NAME_KEY = "name"
    DEVICE_KEY = "device"
    CLASS_KEY = "dataClass"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """
        for key in config:
            self.__dict__["_" + key] = config[key]

        # optional config
        if "_channel" not in self.__dict__:
            self._channel = None

    @property
    def name(self):
        """
        name property getter
        :param self: this
        :return: the name
        """
        return self._name

    @property
    def id(self) -> int:
        """
        id property getter
        :param self: this
        :return: the id
        """
        return self._id

    @property
    def model(self) -> int:
        """
        model property getter
        :param self: this
        :return: the model
        """
        return self._model

    @property
    def device(self) -> int:
        """
        device property getter
        :param self: this
        :return: the device
        """
        return self._device

    @property
    def channel(self) -> int:
        """
        channel property getter
        :param self: this
        :return: the channel
        """
        return self._channel

    @property
    def data_class(self):
        """
        dataClass property getter
        :param self: this
        :return: the dataClass
        """
        # TODO rename config when moved to DB
        # pylint: disable=invalid-name
        return self._dataClass  # NOSONAR (python:S116)

    @data_class.setter
    def data_class(self, data_class):
        """
        dataClass property setter
        :param self: this
        :param: the dataClass
        """
        # TODO rename config when moved to DB
        # pylint: disable=invalid-name
        self._dataClass = data_class  # NOSONAR (python:S116)

    @property
    def key(self):
        """
        key property getter
        :param self: this
        :return: the key
        """
        key = "[" + self._model + "|" + str(self._id)

        if self._channel is not None:
            key = key + "|" + str(self._channel)

        return key + "]"
