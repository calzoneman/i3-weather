2019-01-06
==========

Yahoo deprecated their old weather API in early January 2019, which broke
i3-weather.  There is a replacement API, but it requires manual effort to get an
API key (you have to email them) and doesn't seem like a convenient solution
going forward.  i3-weather has now been updated to retrieve weather from
OpenWeatherMap instead.

**Breaking changes:**

  * OpenWeatherMap requires an API key.  You can register one for free
    [here](https://home.openweathermap.org/users/sign_up)
  * The `{region}` format specifier is no longer supported, since
    OpenWeatherMap's results only include city and country, not state/province
  * The `{visibility}` and `{wind_chill}` format specifiers are no longer
    supported
  * OpenWeatherMap uses a different location model than Yahoo's WOEIDs, so you
    will need to specify the location differently
  * i3-weather now depends on `pyowm` and no longer depends on `requests` or
    `bs4`
