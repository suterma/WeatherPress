# Does a single read and printout of temperature and humidity values from an Si7021 sensor,
# via the Si7021.py module from http://abyz.me.uk/rpi/pigpio/code/Si7021_py.zip
# See https://qrys.ch/reading-14bit-from-an-si7021-temperature-and-humidity-sensor/ for details

import time
import Si7021
import pigpio

pi = pigpio.pi()

if not pi.connected:
   exit(0)
s = Si7021.sensor(pi)

# set the resolution
# 0 denotes the maxium available: Humidity 12 bits, Temperature 14 bits
# See the documentation for more details
s.set_resolution(0)

print("{:.3f} °C".format(s.temperature()))
print("{:.3f} %rH".format(s.humidity()))

s.cancel()
pi.stop()
