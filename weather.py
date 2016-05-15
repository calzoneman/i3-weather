#!/usr/bin/env python3
import argparse
from functools import partial
import json
import logging
import requests
import re
import sys
import time
import urllib.parse

from bs4 import BeautifulSoup

BASE_WEATHER_URL = 'https://query.yahooapis.com/v1/public/yql?'
WEATHER_QUERY = ('select * from weather.forecast where woeid={woeid} '
                 'and u="{unit}"')

def fuzzy_direction(degrees):
    directions = 'N NE E SE S SW W NW'.split()
    index = round(degrees / 45) % 8
    return directions[index]

def arrow_direction(degrees):
    arrows = list('↓↙←↖↑↗→↘')
    index = round(degrees / 45) % 8
    return arrows[index]

def get_weather(woeid, unit, format, timeout=None):
    url = BASE_WEATHER_URL + urllib.parse.urlencode({
        'q': WEATHER_QUERY.format(unit=unit, woeid=woeid),
        'format': 'xml'
    })
    logging.info("Fetching %s" % url)
    try:
        r = requests.get(url, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return ''
    except requests.exceptions.Timeout:
        return ''
    if r.status_code != 200:
        return 'HTTP error: %s' % r.status_code

    s = BeautifulSoup(r.text, 'html.parser')

    data = {}

    # Unit information
    # Prefix each unit key with 'unit_' to prevent ambiguity, e.g.
    # 'temp' vs. 'temperature'
    units = s.find('yweather:units')
    data.update(('unit_' + attr, units.attrs[attr]) for attr in units.attrs)
    # Location information
    data.update(s.find('yweather:location').attrs)
    # Basic conditions - simple description ("Fair", "Cloudy", etc), temperature
    data.update(s.find('yweather:condition').attrs)
    # Wind conditions - speed, chill, direction (degrees)
    # This is a little bit different from the others in that the attributes
    # are prefixed with 'wind_'.  The justification for this is that it doesn't really
    # make sense to ask "what direction does the weather have?", as opposed to
    # "what wind_direction does the weather have?"
    wind = s.find('yweather:wind')
    data.update(('wind_' + attr, wind.attrs[attr]) for attr in wind.attrs)
    data['wind_direction_fuzzy'] = fuzzy_direction(int(data['wind_direction']))
    data['wind_direction_arrow'] = arrow_direction(int(data['wind_direction']))
    # Atmospheric conditions - humidity, visibility, pressure
    data.update(s.find('yweather:atmosphere').attrs)
    # Astronomical conditions - sunrise / sunset
    data.update(fix_sunrise_sunset(s.find('yweather:astronomy').attrs))
    return format.format(**data)

sunrise_sunset_re = re.compile(r'(?P<hour>\d+):(?P<minute>\d+) (?P<am_pm>am|pm)')
def fix_sunrise_sunset(attrs):
    for key, value in attrs.items():
        match = sunrise_sunset_re.fullmatch(value)
        if match:
            yield key, '{hour}:{minute:>02} {am_pm}'.format(**match.groupdict())
        else:
            yield key, value

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('woeid')
    p.add_argument('--format', metavar='F',
                   default='{city}, {region}: {text}, {temp}\u00b0{unit_temperature}',
                   help="format string for output")
    p.add_argument('--position', metavar='P', type=int, default=-2,
                   help="position of output in JSON when wrapping i3status")
    p.add_argument('--unit', metavar='U', default='f',
                   help="unit for temperature")
    p.add_argument('--update-interval', metavar='I', type=int, default=60*3,
                   help="update interval in seconds")
    p.add_argument('--wrap-i3-status', action='store_true')
    p.add_argument('--timeout', metavar='T', type=float, default=2,
                   help="timeout on weather request")
    args = p.parse_args()

    if args.timeout == 0:
        args.timeout = None

    _get_weather = partial(get_weather, args.woeid, args.unit, args.format, timeout=args.timeout)

    if args.wrap_i3_status:
        stdin = iter(sys.stdin.readline, '')

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

                if (time.time() > last_update + args.update_interval or
                        weather['full_text'] == ''):
                    try:
                        weather['full_text'] = _get_weather()
                    except Exception as e:
                        weather['full_text'] = ''
                        print('{}: {}'.format(e.__class__.__name__, e), file=sys.stderr)
                    last_update = time.time()
        except KeyboardInterrupt:
            sys.exit()
    else:
        try:
            print(_get_weather())
        except Exception as e:
            print('{}: {}'.format(e.__class__.__name__, e), file=sys.stderr)
