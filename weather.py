#!/usr/bin/python3
import argparse
from functools import partial
import json
import logging
import requests
import sys
import time

from bs4 import BeautifulSoup

def get_weather(woeid, unit, format):
    url = ('http://weather.yahooapis.com/forecastrss?w={}&u={}'
           ''.format(woeid, unit.lower()))
    logging.info("Fetching %s" % url)
    r = requests.get(url)
    if r.status_code != 200:
        return 'weather: %s' % r.status_code

    s = BeautifulSoup(r.text)
    data = {'unit': unit}
    data.update(s.find('yweather:location').attrs)
    data.update(s.find('yweather:condition').attrs)
    return args.format.format(**data)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('woeid')
    p.add_argument('--format', metavar='F',
                   default='{city}, {region}: {text}, {temp}°{unit}',
                   help="format string for output")
    p.add_argument('--position', metavar='P', type=int, default=-2,
                   help="position of output in JSON when wrapping i3status")
    p.add_argument('--unit', metavar='U', default='f',
                   help="unit for temperature")
    p.add_argument('--update-interval', metavar='I', type=int, default=60*3,
                   help="update interval in seconds")
    p.add_argument('--wrap-i3-status', action='store_true')
    args = p.parse_args()

    _get_weather = partial(get_weather, args.woeid, args.unit, args.format)

    if args.wrap_i3_status:
        stdin = iter(sys.stdin)

        # The first two lines from i3status need to pass through unmodified
        print(next(stdin), end='')
        print(next(stdin), end='')

        last_update = 0
        weather = {'name': 'weather', 'full_text': ''}
        try:
            for line in stdin:
                data = json.loads(line.lstrip(','))
                data.insert(args.position, weather)
                print((',' if line.startswith(',') else '') + json.dumps(data))
                sys.stdout.flush()

                if time.time() > last_update + args.update_interval:
                    weather['full_text'] = _get_weather()
                    last_update = time.time()
        except KeyboardInterrupt:
            sys.exit()
    else:
        print(_get_weather())
