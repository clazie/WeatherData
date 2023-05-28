
# Weatherdata
![CI-CD](https://github.com/clazie/WeatherData/actions/workflows/python-app.yml/badge.svg)

Get Weatherdata from EcoWitt, WeatherUnderground or a JSON-file from a website and store it in influx and/or MQTT.

## Install it
The program need python3 and git installed on your system
``` bash
sudo apt install python3 git
```
To install the program on your linux system call 
``` bash
cd ~
git clone https://github.com/clazie/WeatherData.git
cd WeatherData/
pip install -r requirements.txt
pip install -r requirements-dev.txt
# The same für sudo user, if you plan to use it in roots cron job
sudo pip install -r requirements.txt
sudo pip install -r requirements-dev.txt
```
## Run it
To run it copy default config file,
``` bash
cp config-default.yaml config.yaml
```
edit it to your needs and call 
``` bash
python3 ./src/weatherdata.py
```

## Automate getting weatherdata
To run it every minute call 
``` bash
sudo crontab -e
```
and add a line like
``` crontab
* * * * * /usr/bin/python3 /home/<user>/WeatherData/src/weatherdata.py -c /home/<user>/WeatherData/config.yaml> /dev/null 2>&1
```
Change `<user>` to the user that cloned it from git. The program will run as root user.

## Update it
Change to your program directory and run git pull.
``` bash
cd ~/WeatherData
git pull
```