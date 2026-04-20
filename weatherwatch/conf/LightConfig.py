from util.Logger import logger

__all__ = ["LightConfig"]


@logger
class LightConfig:
    """
    light config data
    """

    ENABLE_KEY = "enable"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[LightConfig.ENABLE_KEY]
