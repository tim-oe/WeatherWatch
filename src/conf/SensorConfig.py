class SensorConfig(object):
    NAME_KEY = 'name'
    DEVICE_KEY = 'device'
    CLASS_KEY = 'dataClass'
    
    """
    sensor config data 
    """
    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """
        for key in config:
            self.__dict__['_' + key] = config[key]
            
    #override
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
    
    @name.setter
    def name(self, name):
        """
        name property setter
        :param self: this
        :param: the name
        """
        self._name = name

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
    def device(self) -> int:
        """
        device property getter
        :param self: this
        :return: the device
        """
        return self._device
    
    @device.setter
    def device(self, device: int):
        """
        device property setter
        :param self: this
        :param: the device
        """
        self._device = device                

    @property
    def channel(self) -> int:
        """
        channel property getter
        :param self: this
        :return: the channel
        """
        return self._channel
    
    @channel.setter
    def channel(self, channel: int):
        """
        channel property setter
        :param self: this
        :param: the channel
        """
        self._channel = channel                        
    
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
        