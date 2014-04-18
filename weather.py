#!/usr/bin/python3
import argparse
import json
import requests
import sys
import time

from bs4 import BeautifulSoup

def get_weather(woeid, unit):
    url = 'http://weather.yahooapis.com/forecastrss?w={}&u={}'.format(woeid, unit)
    r = requests.get(url)
    if r.status_code != 200:
        return 'error'

    s = BeautifulSoup(r.text)
    location = s.find('yweather:location')
    condition = s.find('yweather:condition')
    return '{}, {}: {}, {}\u00b0{}'.format(location['city'], location['region'],
                                           condition['text'], condition['temp'], unit)

WEATHER_JSON = {
    'name': 'weather',
    'full_text': ''
}
WEATHER_TIME = time.time()
UPDATE_INTERVAL = 180

def getline():
    try:
        line = sys.stdin.readline().strip()
        if not line:
            sys.exit(3)
        return line
    except KeyboardInterrupt:
        sys.exit()

def sendline(line):
    sys.stdout.write(line + '\n')
    sys.stdout.flush()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('woeid')
    p.add_argument('--unit', default='f')
    p.add_argument('--wrap-i3-status', action='store_true')
    args = p.parse_args()

    if args.wrap_i3_status:
        print(getline())
        print(getline())

        while True:
            line, prefix = getline(), ''
            if line.startswith(','):
                line, prefix = line[1:], ','

            j = json.loads(line)
            j = j[0:-2] + [WEATHER_JSON] + j[-2:]
            sendline(prefix + json.dumps(j))

            if time.time() - UPDATE_INTERVAL > WEATHER_TIME or WEATHER_JSON['full_text'] == '':
                WEATHER_JSON = {
                    'name': 'weather',
                    # Update the below line to your WOEID and preferred unit of temperature
                    'full_text': get_weather(args.woeid, args.unit)
                }
                WEATHER_TIME = time.time()
    else:
        print(get_weather(args.woeid, args.unit))
