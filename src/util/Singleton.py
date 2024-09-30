class Singleton:
    """
    poor mans singleton imple
    add to top of child class __init__

    if(self._initialized): return
    self._initialized = True
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance
