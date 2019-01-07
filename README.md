i3-weather
==========

Simple Python script for grabbing weather information from OpenWeatherMap and
(optionally) displaying it on your i3 status line.

## Installation

Python 3 is required (I tested this code on Python 3.6).  You can install in a
virtualenv or else install the dependencies through your distribution's package
manager.


    $ virtualenv .env
    $ source .env/bin/activate
    (.env) $ pip install -r requirements.txt

### OpenWeatherMap

i3-weather retrieves weather information from [OpenWeatherMap].  In order to use
it, you'll need to register a (free) account and (free) API key.

[OpenWeatherMap]: https://home.openweathermap.org/users/sign_up

## Usage

### With i3status

In your i3 configuration, update the `bar`'s `status_command` to pipe through
i3-weather:


    bar {
        status_command i3status | /path/to/i3-weather/.env/bin/python /path/to/i3-weather/weather.py --wrap-i3-status --api-key ...
    }

### Standalone

i3-weather can also be invoked without using i3status to print the weather
report in plain text.  This is mostly useful for testing your command line
arguments without having to restart i3 every time, but you could also use it to
check the weather from your terminal.


    $ cd /path/to/i3-weather
    $ .env/bin/python weather.py --api-key ...

### Specifying location

OpenWeatherMap's API supports 3 different ways of providing a location, which
are supported by i3-weather as command-line arguments:

  * `--zip`: look up a city by zip/postal code
    - For countries outside the US, you must also specify `--zip-country`
  * `--city-id`: look up a city by OpenWeatherMap's "City ID".  You can find
    this number in the URL when searching for your location on OpenWeatherMap's
    website (for example, Seattle is `https://openweathermap.org/city/5809844`,
    which corresponds to `--city-id 5809844`).
  * `--place`: look up a location by place name (typically `city,country`), e.g.
    `Seattle,US`

See [the API documentation](https://openweathermap.org/current) for more
information about locations.

### Customizing output format

i3-weather retrieves weather information from OpenWeatherMap for the provided
location and formats the result from a user-provided format string (given with
`--format`).  The default format is `{city}, {country}: {text},
{temp}°{unit_temperature}`, which produces an output similar to `Seattle, US:
light rain, 43°F`.

The default units are imperial (degrees Fahrenheit, wind speed in MPH).  You can
change the temperature and wind speed units to metric with `--unit-temperature
celsius` and `--unit-speed meters_sec`, respectively.

The following format specifiers are supported:

  - `{unit_temperature}` - temperature unit (`F` or `C`)
  - `{unit_pressure}` - pressure unit (`hPa`)
  - `{unit_speed}` - speed unit (`mph` or `m/s`)
  - `{city}` - city name associated with the input location
  - `{country}` - country name associated with the input location
  - `{wind_direction}` - direction (in degrees) of the wind
  - `{wind_direction_fuzzy}` - fuzzy direction of the wind (N, NE, etc.)
  - `{wind_direction_arrow}` - arrow direction of the wind (↓, ↙, etc.)
  - `{wind_speed}` - speed of the wind
  - `{humidity}` - relative humidity
  - `{pressure}` - atmospheric pressure
  - `{sunrise}` - sunrise time
  - `{sunset}` - sunset time
  - `{text}` - basic description of condition (e.g "Fair" or "Partly cloudy")
  - `{temp}` - temperature
