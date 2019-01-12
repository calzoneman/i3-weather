#!/bin/bash

# This is a cheap, unsophisticated substitute for actual software tests...
if [ -z "$OWM_KEY" ]; then
    echo "must set OWM_KEY in order to run tests"
    exit 1
fi

if [ -z "$OWM_CITY_ID" ]; then
    echo "must set OWM_CITY_ID in order to run tests"
    exit 1
fi

.env/bin/python weather.py \
    --api-key $OWM_KEY \
    --city-id $OWM_CITY_ID \
    --format "{city}, {country}: {text}, {temp_f}°F ({temp_c}°C, {temp_k}K), Relative humidity {humidity}%, Wind: {wind_speed_mph} MPH ({wind_speed_ms} m/s) from {wind_direction}° ({wind_direction_arrow} {wind_direction_fuzzy}), Daylight from {sunrise} to {sunset}, Pressure {pressure} millibars"

