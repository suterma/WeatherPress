import smbus
import time
 
# Get I2C bus
bus = smbus.SMBus(1)
bus.write_byte(0x40, 0xF5)
 
time.sleep(0.3)
 
# SI7021 address, 0x40  Read 2 bytes, Humidity
data0 = bus.read_byte(0x40)
data1 = bus.read_byte(0x40)
 
# Convert the data
humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6
 
time.sleep(0.3)
bus.write_byte(0x40, 0xF3)
time.sleep(0.3)
 
# SI7021 address, 0x40 Read data 2 bytes, Temperature
data0 = bus.read_byte(0x40)
data1 = bus.read_byte(0x40)
 
# Convert the data and output it
celsTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
fahrTemp = celsTemp * 1.8 + 32
 
textHumidity = "Relative Humidity is : %.2f%%" %humidity
textCelsTemp = "Temperature in Celsius is : %.2f°C" %celsTemp

print (textHumidity)
print (textCelsTemp)

postTitleHumidity = "%.1f%%" %humidity
postTitleCelsTemp = "%.1f°C" %celsTemp

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc import WordPressPost

xmlRcpApiUrl = 'https://xxx/xmlrpc.php'
username = 'xxx'
password =  'xxx'
blog = Client(xmlRcpApiUrl, username, password)

post = WordPressPost()
post.title = postTitleCelsTemp + " " + postTitleHumidity
post.slug='MY_POST_PERMANENT_LINK'
post.content = textCelsTemp + ' ' + textHumidity
post.id = blog.call(posts.NewPost(post))
post.post_status = 'publish'
blog.call(posts.EditPost(post.id, post))

print(post.title + ' posted to ' + xmlRcpApiUrl)


