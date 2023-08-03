from dotenv import load_dotenv
from weather.weather import Weather
import logging

logging.basicConfig(
    level=logging.INFO,  # Set the desired logging level (INFO, DEBUG, ERROR, etc.)
    format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s",
    filename="logs/app.log",  # File to store the logs (optional)
)


def main():
    print("Welcome to the Weather Forecast Application!")

    print(
        "1. Get Current Weather\n2. Get Weather Forecast\n3. Use Geolocation (Optional)\n4. Change Unit Preference\n5. Exit"
    )

    try:
        weather = Weather()

        while True:
            choice = input("Choose an option: ").strip()
            if not choice.isdigit():
                print("Invalid input provided. Not a valid integer.")
                continue

            choice = int(choice)
            if choice not in [1, 2, 3, 4, 5]:
                print("Invalid input provided. Input choice not exists.")
                continue

            match choice:
                case 1:
                    weather.get_current_weather()

                case 2:
                    weather.get_weather_forecast()

                case 3:
                    weather.get_geolocation_weather()

                case 4:
                    weather.change_unit_preference()

                case 5:
                    quit()
    except Exception as e:
        logging.ERROR(f"Error: {e}")


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    main()
