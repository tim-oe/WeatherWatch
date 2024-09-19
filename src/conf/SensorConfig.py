class SensorConfig(object):
    NAME_KEY = "name"
    DEVICE_KEY = "device"
    CLASS_KEY = "dataClass"

    """
    sensor config data 
    """

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

    # override
    def __str__(self):
        return str(self.__dict__)

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
    def model(self):
        """
        model property getter
        :param self: this
        :return: the model
        """
        return self._model

    @property
    def dataClass(self):
        """
        dataClass property getter
        :param self: this
        :return: the dataClass
        """
        return self._dataClass

    @dataClass.setter
    def dataClass(self, dataClass):
        """
        dataClass property setter
        :param self: this
        :param: the dataClass
        """
        self._dataClass = dataClass

    @property
    def key(self):
        """
        key property getter
        :param self: this
        :return: the key
        """
        key = self._model + "|" + str(self._id)

        if self._channel != None:
            key = key + "|" + str(self._channel)

        return key
