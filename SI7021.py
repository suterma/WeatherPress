import smbus
import time
 
# Get I2C bus
bus = smbus.SMBus(1)
# Measure Relative Humidity, No Hold Master Mode
bus.write_byte(0x40, 0xF5)
 
time.sleep(0.3)
 
# SI7021 address, 0x40  Read 2 bytes, Humidity
msbyte = bus.read_byte(0x40)
lsbyte = bus.read_byte(0x40)
print ("MSB is: " + str(msbyte) + " | LSB is: " + str(lsbyte))
 
# Convert the data
data2byte = msbyte * 256 + lsbyte
print (data2byte) # as raw data
humidity = (data2byte * 125 / 65536.0) - 6
 
time.sleep(0.3)
# Measure Temperature, No Hold Master Mode
bus.write_byte(0x40, 0xF3)
time.sleep(0.3)
 
# SI7021 address, 0x40 Read data 2 bytes, Temperature
msbyte = bus.read_byte(0x40)
lsbyte = bus.read_byte(0x40)
print ("MSB is: " + str(msbyte) + " | LSB is: " + str(lsbyte))

# Convert the data and output it
data2byte = msbyte * 256 + lsbyte
print (data2byte) # as raw data
celsTemp = (data2byte * 175.72 / 65536.0) - 46.85
fahrTemp = celsTemp * 1.8 + 32
 
print ("Relative Humidity is : %.2f %%" %humidity)
print ("Temperature in Celsius is : %.2f C" %celsTemp)
print ("Temperature in Fahrenheit is : %.2f F" %fahrTemp)
