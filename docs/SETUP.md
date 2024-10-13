# System setup

![Stand](img/pi.jpg?raw=true)

## hardwar requirements (also see sensors in README)
- Raspberry PI > 3
    - for dev > Pi 3B+ (remote vscode)
    - testbed > Pi zero (sensor processing and camera)
    - [grove hat](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi_Zero/)
    - [poe+ hat](https://www.raspberrypi.com/products/poe-plus-hat/)


## Software requirements
- [Raspberry PI OS Bookworm](https://www.raspberrypi.com/software/operating-systems/)


## setup steps
- use [sdm](https://github.com/gitbls/sdm) for buring sd image
    - see [sample shell script](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/sdm/image.sh)
- use [ansible](https://docs.ansible.com/) to provision dependencies

## project setup
- project uses poetry for dependency managment
    - [local venv for service set POETRY_VIRTUALENVS_IN_PROJECT=true](https://python-poetry.org/docs/configuration/#virtualenvsin-project)
    - [to load gobal libs like Picamera2 set POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true](https://python-poetry.org/docs/configuration/#virtualenvsoptionssystem-site-packages)
- see [init.sh](/init.sh?raw=true) for sdr and circuit python install
    - it's using pip for some local libs


## database
- for dev leveraged docker container with [compose file](/mariadb-docker-compose.yml?raw=true)
    - to start: ```python3 setup.py mysqlUp``` 
    - to stop:  ```python3 setup.py mysqlDown```
    - app user weather:weather     
- external/prod configuration
    - ```CREATE user 'weather'@'%' identified by 'weather';``` 
    - ```GRANT lock tables, select, insert, delete, update, execute, create temporary tables on *.* to 'weather'@'%';```
    - might want to lock down host to source
- pyway user (for managing DDL)
    - ```CREATE user 'pyway'@'%' identified by 'pyway';``` 
    - ```GRANT ALL PRIVILEGES ON weather.* TO 'pyway'@'%';```
    - might want to lock down host to dev system
- user creds handled with env vars 
    - app WW_DB_USERNAME:WW_DB_PASSWORD
    - [pyway](https://github.com/jasondcamp/pyway?tab=readme-ov-file#configuration)