from dotenv import load_dotenv
import requests
import json
import re
from datetime import datetime
from .enums import TemperatureUnit, SpeedUnit
import os

from .helpers import convert_kelvin_to_celsius, convert_kmph_to_mph
import logging

logger = logging.getLogger(__name__)


class Weather:
    def __init__(self):
        self.__WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
        if not self.__WEATHER_API_KEY:
            logger.error("Weather API key not found.")
            raise ValueError("Env Value : Weather API key not found.")

        self.__API_BASE_URL = os.environ.get("WEATHER_API_BASE_URL")
        if not self.__API_BASE_URL:
            logger.error("Weather API base url not found.")
            raise ValueError("Env Value : Weather API base url not found.")

        self.__GEOLOCATION_URL = os.environ.get("GEOLOCATION_URL")
        if not self.__GEOLOCATION_URL:
            logger.error("Geolocation url not found.")
            raise ValueError("Env Value : Geolocation url not found.")

        self.unit_preference = {
            "temperature": TemperatureUnit.CELSIUS,
            "wind_speed": SpeedUnit.KILOMETERS_PER_HOUR,
        }

    def __get_geocoding_by_zip(self, zip_code):
        try:
            response = requests.get(
                f"{self.__API_BASE_URL}/geo/1.0/zip?zip={zip_code}&appid={self.__WEATHER_API_KEY}"
            )
            content = json.loads(response.content)
            response.raise_for_status()
            return content["lat"], content["lon"]
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(
                f"Error while fetching geocoding data using zip: {e}", exc_info=True
            )
            print(f"Error while fetching geocoding data using zip: {e}")
            return None, None

    def __get_geocoding_by_city(self, city_name):
        try:
            response = requests.get(
                f"{self.__API_BASE_URL}/geo/1.0/direct?q={city_name}&limit={1}&appid={self.__WEATHER_API_KEY}"
            )
            content = json.loads(response.content)
            response.raise_for_status()
            if len(content) == 0:
                return None, None
            return content[0]["lat"], content[0]["lon"]
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(
                f"Error while fetching geocoding data by city name: {e}", exc_info=True
            )
            print(f"Error while fetching geocoding data by city name: {e}")
            return None, None

    def __get_geocoding(self, city_or_zip):
        if re.match(r"^\d{5}$", city_or_zip):
            return self.__get_geocoding_by_zip(city_or_zip)
        elif re.match(r"^[a-zA-Z\s]+$", city_or_zip):
            return self.__get_geocoding_by_city(city_or_zip)
        else:
            logger.warning("Invalid input provided.")
            print("Invalid input provided.")
            return None, None

    def get_current_weather(self, lat=None, lon=None):
        try:
            if not lat and not lon:
                city_or_zip = input("Enter city name or ZIP code: ").strip()
                lat, lon = self.__get_geocoding(city_or_zip)

            if not lat or not lon:
                logger.warning("Couldn't fetch geolocation details.")
                print("Couldn't fetch geolocation details.")
                return
            response = requests.get(
                f"{self.__API_BASE_URL}/data/2.5/weather?lat={lat}&lon={lon}&appid={self.__WEATHER_API_KEY}"
            )
            response.raise_for_status()
            content = json.loads(response.content)
            temp, humidity, wind_speed = (
                content["main"]["temp"],
                content["main"]["humidity"],
                content["wind"]["speed"],
            )
            if self.unit_preference["temperature"] == TemperatureUnit.CELSIUS:
                temp = convert_kelvin_to_celsius(temp)

            if self.unit_preference["wind_speed"] == SpeedUnit.MILES_PER_HOUR:
                wind_speed = convert_kmph_to_mph(wind_speed)

            print(f"Weather in {content['name']}:")
            print(f"Temperature: {temp}{self.unit_preference['temperature'].value}")
            print(f"Humidity: {humidity}%")
            print(
                f"Wind Speed: {wind_speed} {self.unit_preference['wind_speed'].value}"
            )
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(
                f"Error while fetching current weather data: {e}", exc_info=True
            )
            print(f"Error while fetching current weather data: {e}")

    def get_weather_forecast(self):
        try:
            city_or_zip = input("Enter city name or ZIP code: ").strip()
            lat, lon = self.__get_geocoding(city_or_zip)
            if not lat or not lon:
                logger.warning("Couldn't fetch geolocation details.")
                print("Couldn't fetch geolocation details.")
                return
            response = requests.get(
                f"{self.__API_BASE_URL}/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.__WEATHER_API_KEY}"
            )
            response.raise_for_status()
            content = json.loads(response.content)
            forecast_list = content["list"]
            print(f"Weather Forecast for {content['city']['name']}:")
            line_no = 0
            for forecast in forecast_list:
                if line_no == 0:
                    hour = forecast["dt_txt"].split(" ")[1]
                if line_no >= 3:
                    break
                if forecast["dt_txt"].find(hour) > -1:
                    line_no += 1
                    print(
                        f"{line_no}. Date: {forecast['dt_txt'].split(' ')[0]}, ",
                        end="",
                    )
                    temp = forecast["main"]["temp"]
                    if self.unit_preference["temperature"] == TemperatureUnit.CELSIUS:
                        temp = convert_kelvin_to_celsius(temp)
                    print(
                        f"Temperature: {temp}{self.unit_preference['temperature'].value}, ",
                        end="",
                    )
                    print(f"Weather: {forecast['weather'][0]['description']}")
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(
                f"Error while fetching weather forecast data: {e}", exc_info=True
            )
            print(f"Error while fetching weather forecast data: {e}")

    def get_geolocation_weather(self):
        try:
            response = requests.get(self.__GEOLOCATION_URL)
            response.raise_for_status()
            content = response.content.decode().strip()
            lat, lon = content.split(",")

            if not lat or not lon:
                logger.warning("Couldn't fetch current geolocation details.")
                print("Couldn't fetch current geolocation details.")
                return

            self.get_current_weather(lat, lon)

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error(
                f"Error while fetching gelolocation weather data: {e}", exc_info=True
            )
            print(f"Error while fetching gelolocation weather data: {e}")

    def change_unit_preference(self):
        print("1. Celsius (°C)\n2. Fahrenheit (°F)")
        try:
            choice = int(input("Choose your preferred temperature unit: "))
            if choice == 1:
                self.unit_preference["temperature"] = TemperatureUnit.CELSIUS
            elif choice == 2:
                self.unit_preference["temperature"] = TemperatureUnit.FAHRENHEIT
            else:
                print(
                    "Invalid input provided. Entered value is not in the given choice."
                )
                return
        except ValueError as e:
            print("Invalid input provided. Not a valid integer.")
            return

        print("1. km/h\n2. mph")
        try:
            choice = int(input("Choose your preferred wind speed unit: "))
            if choice == 1:
                self.unit_preference["wind_speed"] = SpeedUnit.KILOMETERS_PER_HOUR
            elif choice == 2:
                self.unit_preference["wind_speed"] = SpeedUnit.MILES_PER_HOUR
            else:
                print(
                    "Invalid input provided. Entered value is not in the given choice."
                )
                return
        except ValueError as e:
            print("Invalid input provided. Not a valid integer.")
            return

        print("Unit preferences updated!")
        logger.info("Unit preferences updated!")
