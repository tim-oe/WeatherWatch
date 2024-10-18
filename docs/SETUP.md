# System setup

![PI setup](img/pi.jpg?raw=true)

## hardware requirements (also see sensors in README)
- Raspberry PI > 3
    - for dev > Pi 3B+ (remote vscode)
    - testbed > Pi zero (sensor processing and camera)
    - [grove hat](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi_Zero/)
    - [poe+ hat](https://www.raspberrypi.com/products/poe-plus-hat/)


## Software requirements
- [Raspberry PI OS Bookworm](https://www.raspberrypi.com/software/operating-systems/)
- see ansible playbooks for additional external dependencies
- python lib deps from [pyproject.toml](/pyproject.toml?raw=true)

## setup steps
- used [sdm](https://github.com/gitbls/sdm) for burning sd image
- used [ansible](https://docs.ansible.com/) to provision dependencies
    - [sdr playbook](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/ansible/weather/nesdr.yml)
    - [python deps playbook](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/ansible/weather/python.yml)
    


## project setup
- project uses poetry for dependency managment
    - poetry needs to be manually installed due to [old apt version](https://github.com/pypa/pipx/issues/1481)
    - [local venv for service set POETRY_VIRTUALENVS_IN_PROJECT=true](https://python-poetry.org/docs/configuration/#virtualenvsin-project)
    - [to load gobal libs like Picamera2 set POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true](https://python-poetry.org/docs/configuration/#virtualenvsoptionssystem-site-packages)
- see [init.sh](/init.sh?raw=true) for sdr, project, and circuit python install
    - it's using pip for some local libs, but these should be in he project manifest


## database
- for dev leveraged docker container with [compose file](/mariadb-docker-compose.yml?raw=true)
    - to start: ```python3 setup.py mysqlUp``` 
    - to stop:  ```python3 setup.py mysqlDown```
    - app user weather:weather     
- external/prod setup configuration
    - [mysql ansible playbook](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/ansible/apps/mysql.yml)
    - create db ```create database weather;``` 
    - ```CREATE user 'weather'@'%' identified by 'weather';``` 
    - ```GRANT lock tables, select, insert, delete, update, execute, create temporary tables on weather.* to 'weather'@'%';```
    - might want to lock down host to source
- pyway user (for managing DDL)
    - ```CREATE user 'pyway'@'%' identified by 'pyway';``` 
    - ```GRANT ALL PRIVILEGES ON weather.* TO 'pyway'@'%';```
    - might want to lock down host to dev system
- user creds handled with env vars 
    - app WW_DB_USERNAME:WW_DB_PASSWORD
    - [pyway](https://github.com/jasondcamp/pyway?tab=readme-ov-file#configuration)
- initialize db ```pyway migrate``` 
    