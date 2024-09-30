class Singleton:
    """
    poor man's singleton imple
    https://stackoverflow.com/questions/12305142/issue-with-singleton-python-call-two-times-init

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
