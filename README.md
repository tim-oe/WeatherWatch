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


## Sensors
- [Nooelec RTL-SDR v5](https://www.nooelec.com/store/nesdr-smart-sdr.html?srsltid=AfmBOooo6Krrq7dvl4eQHVzfA-Yd0QMADqy0cH9XJ5qf-dx8T5dQAby2)
- [indoor Thermo-Hygrometer](https://www.sainlogic.com/english/additional-temperature-and-humidity-sensor-for-sainlogic-weather-station-ft0300.html)
- [outdoor sensor](https://www.sainlogic.com/english/transmitter-for-sainlogic-weather-station-ft0310-1.html)
- [Barometric sensor](https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx)


## non pyton libs
- [rtl_433](https://github.com/merbanan/rtl_433)


## python sensor libs
- [BMP 3xx](https://github.com/adafruit/Adafruit_CircuitPython_BMP3XX)
- [PiCamera2](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)


## tests
- all tests:   ```poetry run pytest```
- single test: ```poetry run pytest -v -s <path/to/test/file.py>```


## TODOs
- document system setup
- document cutomizing config
- document service setup
- implement UI    
- [packaging](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)
- profiling
    - [cprofile](https://docs.python.org/3/library/profile.html#module-cProfile)
    - [guide](https://www.turing.com/kb/python-code-with-cprofile)


## faq
- [logging config file](https://gist.github.com/panamantis/5797dda98b1fa6fab2f739a7aacc5e9d)
- [poetry vscode](https://www.markhneedham.com/blog/2023/07/24/vscode-poetry-python-interpreter/)
