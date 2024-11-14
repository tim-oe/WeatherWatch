# System setup

## PI requirements 
- Pi 3B+ or higher
    - remote development via vcode
    - timelapse video processing
- weather only might work with zero
    - used to some stage teting
    - no longevity testing done

## Software requirements
- [Raspberry PI OS Bookworm](https://www.raspberrypi.com/software/operating-systems/)
- [rtl_433 for sensor data ](https://github.com/merbanan/rtl_433)
- [application dependencies](/pyproject.toml?raw=true)
- [opencv-python with no binary dist](https://rockyshikoku.medium.com/use-h264-codec-with-cv2-videowriter-e00145ded181)
    - needed to get native h264 encoding
    - install can take a while
    - [instructions used](https://python-poetry.org/blog/announcing-poetry-1.2.0/#opting-out-of-binary-distributions)

## python sensor libs
- [BMP 3xx](https://github.com/adafruit/Adafruit_CircuitPython_BMP3XX)
- [GPS](https://github.com/adafruit/Adafruit_CircuitPython_GPS)
- [PiCamera2](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)

## System initialization
- used [sdm](https://github.com/gitbls/sdm) for burning sd image
- used [ansible](https://docs.ansible.com/) to provision dependencies
    - [sdr playbook](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/ansible/weather/nesdr.yml)
    - [python deps playbook](https://raw.githubusercontent.com/tim-oe/piImage/refs/heads/main/src/ansible/weather/python.yml)

## weather undergrount data upload
- [register](https://www.wunderground.com/signup)
- [upload protocol](https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US)

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
    - create user ```CREATE user 'weather'@'%' identified by 'weather';``` 
    - grant privileges ```GRANT lock tables, select, insert, delete, update, execute, create temporary tables on weather.* to 'weather'@'%';```
    - might want to lock down host to source
- pyway user (for managing DDL)
    - ```CREATE user 'pyway'@'%' identified by 'pyway';``` 
    - ```GRANT ALL PRIVILEGES ON weather.* TO 'pyway'@'%';```
    - might want to lock down host to dev system
- user creds handled with env vars 
    - app WW_DB_USERNAME:WW_DB_PASSWORD
    - [pyway](https://github.com/jasondcamp/pyway?tab=readme-ov-file#configuration)
- initialize db ```pyway migrate``` 
    
## running tests
- all tests:   ```poetry run pytest```
- single test: ```poetry run pytest -v -s <path/to/test/file.py>```

## faq
- [logging config file](https://gist.github.com/panamantis/5797dda98b1fa6fab2f739a7aacc5e9d)
- [poetry vscode](https://www.markhneedham.com/blog/2023/07/24/vscode-poetry-python-interpreter/)
- [lint sample config](https://github.com/atlassian-api/atlassian-python-api/blob/master/pyproject.toml)
- [pytest setup teardown](https://stackoverflow.com/questions/26405380/how-do-i-correctly-setup-and-teardown-for-my-pytest-class-with-tests)
- [packaging](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)
