# WeatherWatch
raspbery pi based weather data collector using OTC sensors.

![weather station](docs/img/station_full.jpg?raw=true)



https://github.com/user-attachments/assets/523e9238-fdcc-4cb3-9ceb-55d5e1081674



## Motivation
this was spurred by my original [weather station](https://github.com/tim-oe/SkyWeather2) built using a kit from [switchdoclabs](https://github.com/switchdoclabs/SDL_Pi_SkyWeather2). Unfortunately they are no longer producing for the consumer market. The head unit died and the software will not run on latest PI OS. There was certain features and functionality that I wanted to better understand and hopefully improve in.

## functionality
- read and record outdoor weather metrices at a fixed time interval
    - temprature
    - humidity
    - pressure
    - rain fall
    - wind
    - uv
    - illimuation 
- read and record indoor weather metrices at a fixed time interval
    - more than 1 sensor
    - temprature
    - humidity
- take image at a fixed time interval
    - exif tagging
        - gps data
        - weather information
- roll up images into daily timelapse video        
- post weather data to [Weather Underground](https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US)

## Objectivs
- improve python development knowledge
- understand all weather sensor functionality 
- use existing libs as much as possible
- unit testing with at least 80% coverage
- process reliability and longevity
    - no rebooting functionality
    - memory and resource stability
- [poetry](https://python-poetry.org/docs/) for dependancy management 
- [pyway](https://github.com/sergiosbx/pyway) for schema managment
- [sqlalchemy](https://docs.sqlalchemy.org/en/20/) for orm persistence
- configuration overrides external to source code
- extensible sensor configuration

## docs
- [BOM](/docs/BOM.md)
- [setup](/docs/SETUP.md)
- [config](/docs/CONFIG.md)

## TODOs
- image retension policy
- weather underground API
- DB sensor configuration    
- UI
    - [i18n](https://github.com/marcanuy/python-i18n-skel)
    - dynamic data load
    - AQI page
    - sdr sensor config
- profiling
    - [cprofile](https://docs.python.org/3/library/profile.html#module-cProfile)
    - [guide](https://www.turing.com/kb/python-code-with-cprofile)
- [linting](https://github.com/pylint-dev/pylint)
