import logging
import pprint


def logger(cls):
    """
    decorator to add logger and to_string to classes
    """

    def to_string(self):
        return pprint.pformat(self.__dict__)

    setattr(cls, "logger", logging.getLogger(cls.__name__))
    setattr(cls, "__str__", to_string)

    return cls
