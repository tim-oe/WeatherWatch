# WeatherWatch
raspbery pi based weather data collector using OTC sensors.

![weather station](docs/img/station_full.jpg?raw=true)

https://github.com/user-attachments/assets/523e9238-fdcc-4cb3-9ceb-55d5e1081674


## Motivation
this was spurred by my original [weather station](https://github.com/tim-oe/SkyWeather2) built using a kit from [switchdoclabs](https://github.com/switchdoclabs/SDL_Pi_SkyWeather2). Unfortunately they are no longer producing for the consumer market. The head unit died and the software will not run on latest PI OS. There was certain features and functionality that I wanted to better understand and hopefully improve on.

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
- backup db, images, videos to nas 
    - secondary cloud backup handled externally

## Objectivs
- improve python development knowledge
- understand all weather sensor functionality 
- use existing libs as much as possible
- unit testing with at least 80% coverage
    - sonarqube processing
- process reliability and longevity
    - no rebooting functionality
    - memory and resource stability
- [poetry](https://python-poetry.org/docs/) for dependancy management
    - [poetry-up-plugin](https://github.com/MousaZeidBaker/poetry-plugin-up)
- [pyway](https://github.com/sergiosbx/pyway) for schema managment
- [sqlalchemy](https://docs.sqlalchemy.org/en/20/) for orm persistence
- [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/) for WSGI server
- configuration overrides external to source code
- extensible sensor configuration

## docs
- [BOM](/docs/BOM.md)
- [setup](/docs/SETUP.md)
- [config](/docs/CONFIG.md)

## TODOs
- [lightning sensor](https://www.seeedstudio.com/Grove-Lightning-Sensor-AS3935-p-5603.html)
- DB sensor configuration
    - data extension points    
- UI
    - [i18n](https://github.com/marcanuy/python-i18n-skel)
    - sdr sensor config
- profiling
    - [cprofile](https://docs.python.org/3/library/profile.html#module-cProfile)
    - [guide](https://www.turing.com/kb/python-code-with-cprofile)

