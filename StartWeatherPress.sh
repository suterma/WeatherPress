#!/bin/bash
# Prepares the pigpiod daemon and runs the WeatherPress python script

# start the daemon, if not running
if [ps -u root | grep pigpiod -q] then
    echo "starting pigpiod..."
    sudo pigpiod
fi
echo "pigpiod is running."


# start the WeatherPress.py script
python3 WeatherPress.py

# optionally, terminate the pigpiod daemon
# sudo killall pigpiod
