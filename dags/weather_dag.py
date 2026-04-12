import json
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.standard.operators.python import PythonOperator
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENWEATHER_API_KEY")
s3_bucket = os.getenv("S3_BUCKET_NAME")

# Changing kelvin data to celcius
def kelvin_to_celcius(temp_in_kelvin):
    temp_in_celcius = temp_in_kelvin - 273.15
    return round(temp_in_celcius,2)

def etl_weather_data(task_instance):

    data = task_instance.xcom_pull(task_ids='extract_weather_data')
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

    now = datetime.now()
    dt_string = now.strftime(f"%d%m%y%H%M%S")
    dt_string= 'weather_data_raipur_'+dt_string

    # Initializing AWS credentials.
    aws_credentials = {
    "key": os.getenv("key"),
    "secret": os.getenv("secret"),
    "token": os.getenv("token")
    }


    df.to_csv(f's3://{s3_bucket}/{dt_string}.csv', index=False, storage_options = aws_credentials)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 4, 10),
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'weather_dag',
    default_args=default_args,
    schedule='@daily',        # ← changed from schedule_interval
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermap_api',
        endpoint=f'/data/2.5/weather?q=bilaspur&APPID={api_key}'
    )

    extract_weather_data = HttpOperator(
        task_id='extract_weather_data',
        http_conn_id='weathermap_api',
        endpoint=f'/data/2.5/weather?q=bilaspur&APPID={api_key}',
        method='GET',
        response_filter=lambda r: json.loads(r.text),
        log_response=True
    )

    transform_weather_data = PythonOperator(
        task_id='transform_weather_data',
        python_callable=etl_weather_data
    )

    # This show the flow of task initiated
    is_weather_api_ready >> extract_weather_data >> transform_weather_data