#!/bin/bash
# init script to add system and python deps
# that are not handled via ansible scripts
# requires git hub acct and git
# assumes intial install into home dir
#
# https://github.com/merbanan/rtl_433/blob/master/docs/BUILDING.md
# 
mkdir src
cd src
git clone git@github.com:merbanan/rtl_433.git
cd rtl_433/
cmake -DFORCE_COLORED_BUILD:BOOL=ON -GNinja -B build
cmake --build build -j 4
sudo cmake --build build --target install

# pipx apt install is ancient and will only install poetry locally
# this script assumes it's installed 
# possible work around for global https://github.com/pypa/pipx/issues/1481
# https://python-poetry.org/docs/#installing-with-pipx
# circuit pyton install
# https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi
cd ..
git clone git@github.com:tim-oe/WeatherWatch.git
# to keep service defs consistent and not tied to src install location
sudo ln -s "$HOME/src/WeatherWatch" /opt/WeatherWatch
cd WeatherWatch

sudo 
poetry install
# ensure latest
poetry add adafruit-python-shell@latest
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py
