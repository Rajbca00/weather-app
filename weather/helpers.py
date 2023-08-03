import requests


def convert_kelvin_to_celsius(temperature):
    celsius_temperature = round(temperature - 273.15, 2)
    return celsius_temperature


def convert_kmph_to_mph(speed):
    mph = round(speed * 0.6213711922, 2)
    return mph
