import logging
import pprint


def logger(cls):
    def to_string(self):
        return pprint.pformat(self.__dict__)

    setattr(cls, "logger", logging.getLogger(cls.__name__))
    setattr(cls, "__str__", to_string)

    return cls
