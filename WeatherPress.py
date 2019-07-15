# WeatherPress.py - A simple, Raspberry Pi based weather station, that posts
# to a WordPress blog.
# ------------------------------------------------------------------------------

import time
import Si7021
import pigpio

pi = pigpio.pi()
s = Si7021.sensor(pi)

# set the resolution
# 0 denotes the maxium available: Humidity 12 bits, Temperature 14 bits
# See the documentation for more details
s.set_resolution(0)

# get the environment data
temperature = s.temperature()
humidity = s.humidity()

print("{:.2f} °C".format(temperature))
print("{:.2f} %rH".format(humidity))

s.cancel()
pi.stop()

# Post the data to a WordPress blog

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc import WordPressPost

textHumidity = "Relative Humidity is : %.2f%%" %humidity
textTemperature = "Temperature in Celsius is : %.2f°C" %temperature

print (textHumidity)
print (textTemperature)

postTitleHumidity = "%.1f%%" %humidity
postTitleTemperature = "%.1f°C" %temperature

xmlRcpApiUrl = 'https://XXX/xmlrpc.php'
username = 'XXX'
password =  'XXX'
blog = Client(xmlRcpApiUrl, username, password)

print('posting...')

post = WordPressPost()
post.title = postTitleTemperature + " " + postTitleHumidity
post.slug='MY_POST_PERMANENT_LINK'
post.content = textTemperature + ' ' + textHumidity
post.terms_names = {
        'post_tag': ['1.OG', 'Nordseite'],
        'category': ['Aussen'],
}
post.id = blog.call(posts.NewPost(post))
# Always publish these posts
post.post_status = 'publish'
blog.call(posts.EditPost(post.id, post))

# Report success
print(post.title + ' posted to ' + xmlRcpApiUrl)




