#!/usr/bin/env python3
import argparse
from datetime import datetime
from functools import partial
import json
from pyowm import OWM
import sys
import time

def fuzzy_direction(degrees):
    if not degrees:
        return '?'
    directions = 'N NE E SE S SW W NW'.split()
    index = round(degrees / 45) % 8
    return directions[index]

def arrow_direction(degrees):
    if not degrees:
        return '?'
    arrows = list('↓↙←↖↑↗→↘')
    index = round(degrees / 45) % 8
    return arrows[index]

def unix_to_hhmm(ts):
    dt = datetime.fromtimestamp(ts)
    return dt.strftime('%H:%M')

def format_weather(obs, format_str):
    data = {}
    loc = obs.get_location()
    weather = obs.get_weather()

    data['city'] = loc.get_name()
    data['country'] = loc.get_country()
    data['temp_f'] = round(weather.get_temperature(unit='fahrenheit')['temp'])
    data['temp_c'] = round(weather.get_temperature(unit='celsius')['temp'])
    data['temp_k'] = round(weather.get_temperature(unit='kelvin')['temp'])
    data['text'] = weather.get_detailed_status()
    data['humidity'] = weather.get_humidity()
    data['pressure'] = weather.get_pressure()['press']

    wind = weather.get_wind(unit='meters_sec')
    # Wind direction is sometimes unset; I'm assuming this occurs when
    # different weather stations for the same location report the wind
    # blowing in conflicting directions
    data['wind_direction'] = round(wind['deg']) if 'deg' in wind else None
    data['wind_speed_ms'] = round(wind['speed'])
    data['wind_speed_mph'] = round(weather.get_wind(unit='miles_hour')['speed'])
    data['wind_direction_fuzzy'] = fuzzy_direction(data['wind_direction'])
    data['wind_direction_arrow'] = arrow_direction(data['wind_direction'])

    data['sunrise'] = unix_to_hhmm(weather.get_sunrise_time())
    data['sunset'] = unix_to_hhmm(weather.get_sunset_time())
    return format_str.format(**data)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--api-key', type=str, required=True,
                   help='OpenWeatherMap API key')
    p.add_argument('--format', metavar='F',
                   default='{city}, {country}: {text}, {temp_f}°F',
                   help="format string for output")
    p.add_argument('--position', metavar='P', type=int, default=-2,
                   help="position of output in JSON when wrapping i3status")
    p.add_argument('--update-interval', metavar='I', type=int, default=60*10,
                   help="update interval in seconds (default: 10 minutes)")
    p.add_argument('--wrap-i3-status', action='store_true')
    p.add_argument('--zip-country', type=str, default='US',
                   help='set country for zip code lookup (defaults to US)')

    loc = p.add_mutually_exclusive_group(required=True)
    loc.add_argument('--zip', type=str,
                   help='retrieve weather by postal/zip code')
    loc.add_argument('--city-id', type=int, help='retrieve weather by city ID')
    loc.add_argument('--place', type=str,
                   help='retrieve weather by city,country name')
    args = p.parse_args()

    owm = OWM(API_key=args.api_key, version='2.5')

    if args.zip:
        get_observation = partial(owm.weather_at_zip_code, args.zip,
                                  args.zip_country)
    elif args.city_id:
        get_observation = partial(owm.weather_at_id, args.city_id)
    else:
        get_observation = partial(owm.weather_at_place, args.place)

    def _get_weather():
        return format_weather(get_observation(), args.format)

    if args.wrap_i3_status:
        stdin = iter(sys.stdin.readline, '')

        header = next(stdin)
        if json.loads(header)['version'] != 1:
            raise Exception('Unrecognized version of i3status: ' +
                            header.strip())

        print(header, end='')
        # First line after header is '[' (open JSON array)
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
                        print('{}: {}'.format(e.__class__.__name__, e),
                              file=sys.stderr)
                    last_update = time.time()
        except KeyboardInterrupt:
            sys.exit()
    else:
        try:
            print(_get_weather())
        except Exception as e:
            print('{}: {}'.format(e.__class__.__name__, e), file=sys.stderr)
