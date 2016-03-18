i3-weather
==========

Simple Python script for grabbing weather information fron Yahoo and
(optionally) outputting it to your i3 status line.

Requires `requests` and `BeautifulSoup4`, both installable with `pip`.  Tested with Python 2.7.6 and Python 3.4.0 on Arch Linux.

To use this with i3, open `.i3/config` and update `status_command` to
pipe through `weather.py --wrap-i3-status`. Example:

    bar {
        status_command i3status | /path/to/weather.py --wrap-i3-status 12773700
        ...
    }

### Output Format

The script retrieves various data about the weather conditions for the provided WOEID.  You can use various format specifiers with the `--format` flag to customize the output.  The default format is `{city}, {region}: {text}, {temp}°{unit_temperature}`, which produces an output similar to `Auburn, AL: Fair, 75°F`.

Your preferred unit of temperature can be set with `--unit f` or `--unit c` (this will also affect the other units: passing `--unit c` will also cause the speed unit to be `km/h` instead of `mph`)

The following format specifiers are supported:

  - `{unit_temperature}` - temperature unit (`F` or `C`)
  - `{unit_distance}` - distance unit (`mi` or `km`)
  - `{unit_pressure}` - pressure unit (`in` or `mb`)
  - `{unit_speed}` - speed unit (`mph` or `km/h`)
  - `{city}` - city associated with the input WOEID
  - `{region}` - region (state/province) associated with the input WOEID
  - `{country}` - country associated with the input WOEID
  - `{wind_chill}` - windchill temperature
  - `{wind_direction}` - direction (in degrees) of the wind
  - `{wind_direction_fuzzy}` - fuzzy direction of the wind (N, NE, etc.)
  - `{wind_direction_arrow}` - arrow direction of the wind (↓, ↙, etc.)
  - `{wind_speed}` - speed of the wind
  - `{humidity}` - relative humidity
  - `{visibility}` - visibility (I have no idea how this is measured)
  - `{pressure}` - atmospheric pressure
  - `{sunrise}` - sunrise time
  - `{sunset}` - sunset time
  - `{text}` - basic description of condition (e.g "Fair" or "Partly cloudy")
  - `{temp}` - temperature
