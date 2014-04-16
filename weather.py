#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup

def get_weather(woeid, unit='f'):
    url = 'http://weather.yahooapis.com/forecastrss?w={}&u={}'.format(woeid, unit)
    r = requests.get(url)
    if r.status_code != 200:
        return 'error'

    s = BeautifulSoup(r.text)
    location = s.find('yweather:location')
    condition = s.find('yweather:condition')
    return '{}, {}: {}, {}\u00b0{}'.format(location['city'], location['region'],
                                           condition['text'], condition['temp'], unit)

if __name__ == '__main__':
    print(get_weather('12773700', 'f'))
