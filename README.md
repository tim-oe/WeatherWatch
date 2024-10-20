# WeatherWatch
raspbery pi based weather data collector using OTC sensors.


## Motivation
this was spurred by my original [weather station](https://github.com/tim-oe/SkyWeather2) built using kit from [switchdoclabs](https://github.com/switchdoclabs/SDL_Pi_SkyWeather2). Unfortunately they are no longer producing for the consumer market. The head unit died and the software will not run on latest PI OS


## Objectivs
- use the [switchdoc code](https://github.com/switchdoclabs/SDL_Pi_SkyWeather2) as a base line
- use existing libs as much as possible
- implement with OOP best practices
- implements unit tests with at least 80% coverage
- use [pyway](https://github.com/sergiosbx/pyway) for schema versioning
- use [sqlalchemy](https://docs.sqlalchemy.org/en/20/) for data persistance
- standard [logging](https://docs.python.org/3/library/logging.html)
- use [poetry](https://python-poetry.org/docs/) for dependancy management 
- allow configuration overrides
- make hooks for additional sensor


## non python libs
- [rtl_433](https://github.com/merbanan/rtl_433)


## python sensor libs
- [BMP 3xx](https://github.com/adafruit/Adafruit_CircuitPython_BMP3XX)
- [PiCamera2](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)


## docs
- [BOM](/docs/BOM.md)
- [setup](/docs/SETUP.md)
- [config](/docs/CONFIG.md)


## tests
- all tests:   ```poetry run pytest```
- single test: ```poetry run pytest -v -s <path/to/test/file.py>```


## TODOs
- document service setup
- implement UI
    - [i18n](https://github.com/marcanuy/python-i18n-skel)
- time lapse video
- image retension policy
- extensible sensor configuration    
- [packaging](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)
- profiling
    - [cprofile](https://docs.python.org/3/library/profile.html#module-cProfile)
    - [guide](https://www.turing.com/kb/python-code-with-cprofile)
- [linting](https://github.com/pylint-dev/pylint)

## faq
- [logging config file](https://gist.github.com/panamantis/5797dda98b1fa6fab2f739a7aacc5e9d)
- [poetry vscode](https://www.markhneedham.com/blog/2023/07/24/vscode-poetry-python-interpreter/)
- [lint sample config](https://github.com/atlassian-api/atlassian-python-api/blob/master/pyproject.toml)
