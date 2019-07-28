#!/usr/bin/env python

# Si87021.py
# Public Domain
# 2016-05-07

import time
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

"""
Code to read the Si7021 temprature and relative humidity sensor.

The sensor uses I2C to communicate.

Code      Command

0xE5      Measure Relative Humidity, Hold Master Mode
   MSB LSB CRC

0xF5      Measure Relative Humidity, No Hold Master Mode
   MSB LSB CRC

0xE3      Measure Temperature, Hold Master Mode
   MSB LSB CRC

0xF3      Measure Temperature, No Hold Master Mode
   MSB LSB CRC

0xE0      Read Temperature Value from Previous RH Measurement
   MSB LSB

0xFE      Reset
   ---

0xE6 VAL  Write RH/T User Register 1

   D7   D6   D5   D4   D3   D2   D1   D0
   RES1 VDDS RSVD RSVD RSVD HTRE RSVD RES0

   RES:  RH/T 0 12/14, 1 8/12, 2 10/13, 3 11/11
   VDDS: 0 okay, 1 low
   HTRE: 0 heater disable, 1 heater enable

0xE7      Read RH/T User Register 1
   VAL

0x51 VAL  Write Heater Control Register

   D7   D6   D5   D4   D3   D2   D1   D0
   RSVD RSVD RSVD RSVD HTR3 HTR2 HTR1 HTR0

   HTR: mA 0 3.09, 1 9.18, 2 15.24, 4 27.39, 8 51.69, 15 94.2

0x11      Read Heater Control Register
   VAL

0xFA 0x0F Read Electronic ID 1st Byte
   SNA_3 CRC SNA_2 CRC SNA_1 CRC SNA_0 CRC

0xFC 0xC9 Read Electronic ID 2nd Byte
   SNB_3 SNB_2 CRC SNB_1 SNB_0 CRC

   SNB_3: 0x00 sample, 0x0D 7013, 0x14 7020, 0x15 7021, 0xFF sample

0x84 0xB8 Read Firmware Revision
   REV

   REV: 0xFF 1.0, 0x20 2.0

"""

class sensor:

   """
   A class to read the Si7021 I2C temperature and humidity sensor.
   """
   def __init__(self, pi, bus=1, addr=0x40):
      """
      Instantiate with the Pi.

      Optionally the I2C bus may be specified, default 1.

      Optionally the I2C address may be specified, default 0x40.
      """
      self.pi = pi
      self._h = pi.i2c_open(bus, addr)

   def cancel(self):
      """
      Cancels the sensor and releases resources.
      """
      self.pi.i2c_close(self._h)

   def temperature(self):
      """
      Returns the temperature in degrees centigrade.  If the CRC
      is incorrect 999 is returned.
      """
      self.pi.i2c_write_device(self._h, [0xF3]) # T no hold
      time.sleep(0.1)
      c, t = self.pi.i2c_read_device(self._h, 3) # msb, lsb, checksum
      if self._crc(t) == 0:
         t_val = (t[0]<<8) + t[1]
         T = ((175.72 * t_val)/65536.0) - 46.85
      else:
         T = 999
      return T

   def humidity(self):
      """
      Returns the relative humidity.  If the CRC is incorrect
      999 is returned.
      """
      self.pi.i2c_write_device(self._h, [0xF5]) # RH no hold
      time.sleep(0.1)
      c, rh = self.pi.i2c_read_device(self._h, 3) # msb, lsb, checksum
      if self._crc(rh) == 0:
         rh_val = (rh[0]<<8) + rh[1]
         RH = ((125.0 * rh_val)/65536.0) - 6.0
      else:
         RH = 999
      return RH

   def switch_heater_on(self):
      """
      Switches the heater on.
      """
      # read register and only update heater bit
      self.pi.i2c_write_device(self._h, [0xE7])
      c, val = self.pi.i2c_read_device(self._h, 1)
      v = (val[0] & 0xFB) | 4
      self.pi.i2c_write_device(self._h, [0xE6, v])

   def switch_heater_off(self):
      """
      Switches the heater off.
      """
      # read register and only update heater bit
      self.pi.i2c_write_device(self._h, [0xE7])
      c, val = self.pi.i2c_read_device(self._h, 1)
      v = (val[0] & 0xFB)
      self.pi.i2c_write_device(self._h, [0xE6, v])

   def set_resolution(self, res):
      """
      Sets the resolution of temperature and humidity readings.

      0 : Humidity 12 bits,  Temperature 14 bits
      1 : Humidity  8 bits,  Temperature 12 bits
      2 : Humidity 10 bits,  Temperature 13 bits
      3 : Humidity 11 bits,  Temperature 11 bits
      """
      # read register and only update resolution bits
      self.pi.i2c_write_device(self._h, [0xE7])
      c, val = self.pi.i2c_read_device(self._h, 1)
      v = (val[0] & 0x7E) | (res & 1) | ((res & 2)<<6)
      self.pi.i2c_write_device(self._h, [0xE6, v])

   def get_resolution(self):
      """
      Gets the resolution of temperature and humidity readings.

      0 : Humidity 12 bits,  Temperature 14 bits
      1 : Humidity  8 bits,  Temperature 12 bits
      2 : Humidity 10 bits,  Temperature 13 bits
      3 : Humidity 11 bits,  Temperature 11 bits
      """
      self.pi.i2c_write_device(self._h, [0xE7])
      c, val = self.pi.i2c_read_device(self._h, 1)
      v = ((val[0]&128)>>6) | (val[0]&1)
      return v

   def set_heater_level(self, level):
      """
      Sets the heating level to be used if the heater
      is switched on.

       0:  3.09 mA
       1:  9.18 mA
       2: 15.24 mA
       4: 27.39 mA
       8: 51.69 mA
      15: 94.20 mA

      I don't know what happens for a value other than those shown.
      """
      # read register and only update heater bits
      self.pi.i2c_write_device(self._h, [0x11])
      c, val = self.pi.i2c_read_device(self._h, 1)
      v = (val[0] & 0xF0) | (level & 0x0F)
      self.pi.i2c_write_device(self._h, [0x51, v])

   def get_heater_level(self):
      """
      Gets the heating level to be used if the heater
      is switched on.

       0:  3.09 mA
       1:  9.18 mA
       2: 15.24 mA
       4: 27.39 mA
       8: 51.69 mA
      15: 94.20 mA

      I don't know what happens for a value other than those shown.
      """
      self.pi.i2c_write_device(self._h, [0x11])
      c, level = self.pi.i2c_read_device(self._h, 1) # level
      return level[0]&0x0F

   def firmware_revision(self):
      """
      Returns the firmware revision.

      A value of 0xFF means revision 1.0, a value of 0x20 means
      revision 2.0.
      """
      self.pi.i2c_write_device(self._h, [0x84, 0xB8])
      c, rev = self.pi.i2c_read_device(self._h, 1) # rev
      return rev[0]

   def electronic_id_1(self):
      """
      Returns the first four bytes of the electronic Id.
      If the CRC is incorrect 0 is returned.
      """
      self.pi.i2c_write_device(self._h, [0xFA, 0x0F])
      c, id1 = self.pi.i2c_read_device(self._h, 8) # id1
      if self._crc([id1[0], id1[2], id1[4], id1[6]]) == id1[7]:
         return (id1[0]<<24)|(id1[2]<<16)|(id1[4]<<8)|id1[6]
      else:
         return 0

   def electronic_id_2(self):
      """
      Returns the second four bytes of the electronic Id.
      If the CRC is incorrect 0 is returned.
      """
      self.pi.i2c_write_device(self._h, [0xFC, 0xC9])
      c, id2 = self.pi.i2c_read_device(self._h, 6) # id2
      if self._crc([id2[0], id2[1], id2[3], id2[4]]) == id2[5]:
         return (id2[0]<<24)|(id2[1]<<16)|(id2[3]<<8)|id2[4]
      else:
         return 0

   def _crc(self, data):
      """
      """
      rem = 0
      for b in data:
         rem ^= b
         for bit in range(8):
            if rem & 128:
               rem = (rem << 1) ^ 0x31
            else:
               rem = (rem << 1)
      return rem & 0xFF

if __name__ == "__main__":

   import time
   import Si7021
   import pigpio

   pi = pigpio.pi()

   if not pi.connected:
      exit(0)

   s = Si7021.sensor(pi)

   s.set_resolution(0)
   print("res=", s.get_resolution())

   stop = time.time() + 10

   print("revision={:x} id1={:08x} id2={:08x}".format(s.firmware_revision(),
      s.electronic_id_1(), s.electronic_id_2()))

   while time.time() < stop:

      print("{:.2f} {:.2f}".format(s.temperature(), s.humidity()))

      time.sleep(1)

   s.cancel()

   pi.stop()

