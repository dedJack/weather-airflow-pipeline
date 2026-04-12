# Weather ETL Pipeline — Raipur/Bilaspur

An end-to-end data pipeline that pulls live weather data from the OpenWeather API, transforms it, and loads it into AWS S3 as a CSV file — all orchestrated through Apache Airflow running on an AWS EC2 instance.

I built this to get hands-on with data engineering fundamentals: working with REST APIs, cloud storage, and workflow orchestration in a real environment rather than just locally.

---

## What It Does

Every day, the pipeline:
1. Checks if the OpenWeather API is reachable (HTTP Sensor)
2. Fetches current weather data for Bilaspur, India
3. Transforms raw JSON into a clean, structured format (converts Kelvin → Celsius, parses timestamps, etc.)
4. Saves the result as a timestamped CSV file in an S3 bucket

Each run produces a file like: `weather_data_raipur_120426143022.csv`

---

## Tech Stack

- **Python 3.12**
- **Apache Airflow 3.x** — pipeline orchestration
- **OpenWeather API** — weather data source
- **AWS EC2** — where Airflow runs
- **AWS S3** — where the output CSVs land
- **pandas** — data transformation
- **s3fs / aiobotocore** — writing directly to S3 from pandas

---

## Project Structure

```
weather-airflow-pipeline/
├── dags/
│   └── weather_dag.py       # Main DAG — extract, transform, load
├── src/
│   └── main.py              # Standalone extraction/transformation script
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md
```

---

## DAG Overview

```
is_weather_api_ready >> extract_weather_data >> transform_weather_data
```

| Task | Type | What it does |
|------|------|--------------|
| `is_weather_api_ready` | HttpSensor | Pings the API, waits until it responds |
| `extract_weather_data` | HttpOperator | Makes GET request, returns JSON via XCom |
| `transform_weather_data` | PythonOperator | Cleans data, builds DataFrame, uploads to S3 |

---

## Output CSV Columns

| Column | Description |
|--------|-------------|
| city | City name from API response |
| Description | Weather condition (e.g., "haze", "clear sky") |
| Temperature (C) | Actual temperature |
| Feels like (C) | Feels like temperature |
| Minimum temp (C) | Min temp at time of record |
| Maximum temp (C) | Max temp at time of record |
| Pressure | Atmospheric pressure (hPa) |
| Humidity | Humidity percentage |
| Wind speed | Wind speed in m/s |
| Sunrise (Local Time) | Sunrise time adjusted to local timezone |
| Sunset (Local Time) | Sunset time adjusted to local timezone |
| Time of record | When the reading was taken (local time) |
| Country | Country code |

---

## How to Run This Yourself

Fair warning — this project runs on AWS (EC2 + S3), so you'll need an AWS account. The free tier covers most of this if you're just testing, but do keep an eye on costs.

### Prerequisites

- AWS account with an EC2 instance (Ubuntu 22.04/24.04) and an S3 bucket
- Python 3.12 installed on the instance
- OpenWeather API key — free at [openweathermap.org](https://openweathermap.org/api)

---

### Step 1 — Clone the repo

SSH into your EC2 instance, then:

```bash
git clone https://github.com/YOUR_USERNAME/weather-airflow-pipeline.git
cd weather-airflow-pipeline
```

---

### Step 2 — Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Note:** `s3fs`, `aiobotocore`, and `botocore` have strict version compatibility. The versions in `requirements.txt` are pinned to what works together — don't upgrade them individually or you'll run into dependency conflicts.

---

### Step 3 — Set up environment variables

```bash
cp .env.example .env
nano .env
```

Fill in your real values:

```
OPENWEATHER_API_KEY=your_openweather_api_key
S3_BUCKET_NAME=your_s3_bucket_name
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_SESSION_TOKEN=your_aws_session_token
```

> If you're using long-term IAM credentials (not temporary session credentials), you can leave `AWS_SESSION_TOKEN` blank.

---

### Step 4 — Set up Airflow

```bash
export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create \
    --username admin \
    --password admin \
    --firstname Your \
    --lastname Name \
    --role Admin \
    --email your@email.com
```

Copy the DAG into Airflow's DAGs folder:

```bash
cp dags/weather_dag.py ~/airflow/dags/
```

---

### Step 5 — Configure the HTTP Connection in Airflow

The DAG uses `http_conn_id='weathermap_api'` — you need to register this in Airflow.

1. Start the Airflow webserver: `airflow webserver --port 8080`
2. Go to **Admin → Connections → Add Connection**
3. Fill in:
   - **Connection ID:** `weathermap_api`
   - **Connection Type:** `HTTP`
   - **Host:** `https://api.openweathermap.org`

---

### Step 6 — Start Airflow and trigger the DAG

In one terminal:
```bash
airflow webserver --port 8080
```

In another:
```bash
airflow scheduler
```

Open `http://your-ec2-public-ip:8080` in your browser, find `weather_dag`, and either wait for the daily schedule or trigger it manually.

---

### Step 7 — Verify the output

Go to your S3 bucket in the AWS console — you should see a new CSV file named something like `weather_data_raipur_120426143022.csv`.

---

## Common Issues

**DAG not showing up in Airflow UI**
Make sure the DAG file is in `~/airflow/dags/` and that the scheduler is running.

**API key not loading**
Double-check that your `.env` file is in the same directory you're running from, and that `python-dotenv` is installed.

---

## AWS Setup Tips

- Create an **IAM user** with only `S3FullAccess` — don't use your root account credentials
- Make sure your EC2 **security group** allows inbound traffic on port `8080` so you can access the Airflow UI
- **Stop your EC2 instance** when you're not using it to avoid unnecessary charges

---

## If You Just Want to See It Working

Since this requires AWS infrastructure, here's proof it works:
### Tasks running insdie DAG
<img width="1265" height="821" alt="weather_dag-graph" src="https://github.com/user-attachments/assets/bb7956e9-0c59-4106-bdbb-d8aa0b08e42e" />

### Data Stored in CSV format in S3 bucket
<img width="1919" height="359" alt="image" src="https://github.com/user-attachments/assets/c3f925fc-452c-4056-8ff3-a26bc2810547" />


---

## Author

**Your Name**  
[LinkedIn](https://linkedin.com/in/amanchoudhary11) · [GitHub](https://github.com/dedJack)
