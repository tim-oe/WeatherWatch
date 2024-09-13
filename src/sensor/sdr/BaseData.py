from datetime import datetime

class BaseData(object):

    # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    MODEL_KEY = 'model'

    """
    base sensor data 
    """
    def __init__(self, 
                 timeStamp=None,
                 id=None,
                 batteryOK = False,
                 mic = None,
                 mod = None,
                 freq = None,
                 rssi = None,
                 noise = None,
                 snr = None):
        """
        ctor
        :param self: this
        """
        self.timeStamp = timeStamp
        self.id = id
        self.batteryOk = batteryOK
        self.mic = mic
        self.mod = mod
        self.freq = freq
        self.rssi = rssi
        self.noise = noise
        self.snr = snr

    #override
    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def baseDecoder(o: 'BaseData' , d: dict):
        try:
            o.timeStamp = datetime.strptime(d['time'], BaseData.DATE_FORMAT)
            # TODO will drive instance type...
            o.model = d[BaseData.MODEL_KEY]
            o.id = int(d['id'])
            o.batteryOk = (d['battery_ok'] == 1)
            o.mic = d['mic']
            o.mod = d['mod']
            o.freq = d['freq']
            o.rssi = d['rssi']
            o.noise = d['noise']
            o.snr = d['snr']
        except Exception as e:
            print("BD wtf" + str(e))            
            #raise Exception('failed to parse ' + str(d)) from e
            
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
        return self._snr
    
    @noise.setter
    def noise(self, noise):
        """
        noise property setter
        :param self: this
        :param: the noise
        """
        self._noise = noise                                                                       