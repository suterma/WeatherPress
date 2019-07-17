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

print("{:.3f} °C".format(temperature) + " | {:.3f} %rH".format(humidity))

s.cancel()
pi.stop()

# Post the data to a WordPress blog

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc import WordPressPost

textHumidity = "Relative Humidity is : %.3f %%rH" %humidity
textTemperature = "Temperature in Celsius is : %.3f °C" %temperature

print('preparing post...')

import yaml
with open("WeatherPress.config.yml", "r") as configFile:
    config = yaml.safe_load(configFile)

blog = Client(config['WordPress']['xmlRcpApiUrl'],
              config['WordPress']['username'],
              config['WordPress']['password'])

print('posting...')

post = WordPressPost()
# Create a title with some simple styling classes
post.title = ("{:.1f} <span class='unity'>°C</span>".format(temperature) +
              "&nbsp;&nbsp;&nbsp;"+
              "{:.0f} <span class='unity'>%rH</span>".format(humidity))
post.content = textTemperature + ' ' + textHumidity
post.terms_names = {
        'post_tag': [config['WordPress']['tag']],
        'category': [config['WordPress']['category']],
}
post.id = blog.call(posts.NewPost(post))
# Always publish these posts
print('publishing...')
post.post_status = 'publish'
blog.call(posts.EditPost(post.id, post))

# Report success
print(post.title + ' publicly posted to ' + config['WordPress']['xmlRcpApiUrl'])
