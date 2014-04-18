i3-weather
==========

Simple Python script for grabbing weather information fron Yahoo and
(optionally) outputting it to your i3 status line.

To use this with i3, open `.i3/config` and update `status_command` to
pipe through `weather.py --wrap-i3-status`. Example:

    bar {
        status_command i3status | /path/to/weather.py --wrap-i3-status 12773700
        ...
    }
