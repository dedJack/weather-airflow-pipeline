import pandas as pd
import json
import requests
from datetime import datetime, UTC, timedelta

# city_name = "bilaspur"
base_url = "https://api.openweathermap.org/data/2.5/weather?q="

with open("credentials.txt","r") as f:
    apikey= f.read()


def kelvin_to_celcius(temp_in_kelvin):
    temp_in_celcius = temp_in_kelvin - 273.15
    return round(temp_in_celcius,2)

def etl_weather_data(city_name):

    # Full Url of openweatherapi
    full_url = base_url + city_name + "&appid=" + apikey
    raw_data = requests.get(full_url)
    data = raw_data.json()
    # print(data)


    city = data['name']
    weather_description = data['weather'][0]['description']
    actual_temp = kelvin_to_celcius(data['main']['temp'])
    feels_like_temp = kelvin_to_celcius(data['main']['feels_like'])
    minimum_temp = kelvin_to_celcius(data['main']['temp_min'])
    maximum_temp = kelvin_to_celcius(data['main']['temp_max'])
    pressure = data['main']['pressure'] 
    humidity = data['main']['humidity'] 
    wind_speed = data['wind']['speed']
    sunrise = datetime.fromtimestamp(data['sys']['sunrise']+data['timezone']) 
    sunset = datetime.fromtimestamp(data['sys']['sunset']+data['timezone']) 
    country = data['sys']['country']
    time_of_record = datetime.fromtimestamp(data['dt']+data['timezone']) 

    transformed_data = {
        "city":city,
        "Description":weather_description,
        "Temperature (C)": actual_temp,
        "Feels like (C)":feels_like_temp,
        "Minimum temp (C)":minimum_temp,
        "Maximum temp (C)": maximum_temp,
        "Pressure":pressure,
        "Humidity":humidity,
        "Wind speed":wind_speed,
        "Sunrise (Local Time)":sunrise,
        "Sunset (Local Time)":sunset,
        "Time of record":time_of_record,
        "Country":country
    }

    # Transforming the data into List, then we create a dataframe from List.
    transformed_data_list = [transformed_data]
    df = pd.DataFrame(transformed_data_list)

    df.to_csv(f'weather_data_{city_name}.csv', index=False)

etl_weather_data("raipur")
