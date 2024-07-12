
# Sales Data ETL Project

This project sets up an ETL pipeline for processing sales data using Apache Airflow, Docker, and PostgreSQL. The pipeline extracts, transforms, and loads data from CSV files into a PostgreSQL database.

## Project Structure

```
sales_data/
│
├── dags/
│   └── events_dag.py
│
├── etl/
│   ├── category_tree/
│   ├── item_properties/
├───├── vehicle_data/
│   │   ├── config/
│   │   │   ├── data_type_mappings.json
│   │   ├── main.py
│   ├── kaggle_pipeline/
│       ├── __pycache__/
│       ├── extract.py
│       ├── load.py
│       ├── transform.py
│       └── utils.py
│
├── logs/
├── .DS_Store
├── Dockerfile
├── README.md
├── airflow.cfg
├── docker-compose.yml
├── docker-compose2.yml
├── requirements.txt
└── webserver_config.py
```

## Prerequisites

- Docker
- Docker Compose
- Python 3.7 or higher

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/sales_data.git
cd sales_data
```

### 2. Set Environment Variable

Ensure the `AIRFLOW_PROJ_DIR` and `HOME`  environment variable is set to the project root directory:

```bash
export AIRFLOW_PROJ_DIR=$(pwd)
echo $AIRFLOW_PROJ_DIR
export HOME=$(~)
echo $HOME
```

### 3. Build and Start the Docker Containers

```bash
docker-compose -f docker-compose.yaml up -d
```

This command will start the PostgreSQL database, redis, Airflow webserver, scheduler, worker, trigger and create container's network.

### 4. Verify Directory Mounts

To ensure the directories are correctly mounted, you can enter the Airflow webserver container and list the contents of the directories:

```bash
docker-compose exec -it CONTAINER_ID_FOR_WEBSERVER /bin/bash
ls /opt/airflow/etl/vehicle_data/config
```

### 5. Access the Airflow Web Interface

Open your browser and navigate to `http://localhost:8080`. You should see the Airflow web interface.

### 6. Trigger the DAG

In the Airflow web interface, you can manually trigger the DAG or wait for the scheduled run.

## Project Components

### 1. `docker-compose.yaml`

Defines the services for PostgreSQL and Apache Airflow, including environment variables and volume mounts.

```yaml
version: '3.8'
services:
  pg-db:
    image: postgres:latest
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sales_data
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql/data

  webserver:
    image: apache/airflow:2.3.0
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__CORE__EXECUTOR: 'LocalExecutor'
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: 'postgresql+psycopg2://admin:password@pg-db/sales_data'
      AIRFLOW__WEBSERVER__WEB_SERVER_PORT: 8080
      AIRFLOW__CORE__FERNET_KEY: 'wKs35lvEqa8EZR41DMgJi3hDgW3h9Jr_ckRkxRTtuF4='
      AIRFLOW_PROJ_DIR: '/opt/airflow'
    ports:
      - "8080:8080"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/opt/airflow
    depends_on:
      - pg-db

  scheduler:
    image: apache/airflow:2.3.0
    environment:
      AIRFLOW__CORE__EXECUTOR: 'LocalExecutor'
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: 'postgresql+psycopg2://admin:password@pg-db/sales_data'
      AIRFLOW_PROJ_DIR: '/opt/airflow'
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/opt/airflow
    depends_on:
      - pg-db
    command: scheduler

volumes:
  pg-data:
    driver: local
  airflow_dags:
    driver: local
  airflow_logs:
    driver: local
  airflow_plugins:
    driver: local
```

### 2. `events_dag.py`

Contains the Airflow DAG that defines the ETL process.

```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ilyas',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'events_etl_DAG',
    default_args=default_args,
    description='ETL of events table',
    schedule_interval=timedelta(days=1),
)

run_etl_task = BashOperator(
    task_id='run_events_etl',
    bash_command="cd /opt/airflow/etl/vehicle_data/config && python3 main.py",
    dag=dag,
)

run_etl_task
```

### 3. `main.py`

Contains the main ETL logic, including extracting data, transforming it, and loading it into PostgreSQL.

```python
# vehicle_data/config/main.py

from etl.load import Loader
from etl.extract import DataExtractor
from loguru import logger

logger.add("file_{time}.log", rotation="10MB")

def main_etl_function():
    # Define paths and database URL
    dataset = 'retailrocket/ecommerce-dataset'
    dataset_dir = '/opt/airflow/etl/vehicle_data/config'
    file_paths = [f'{dataset_dir}/events1.csv', f'{dataset_dir}/events2.csv']  # Update with your actual file paths
    db_url = 'postgresql://admin:password@pg-db:5432/sales_data'  # Update with your actual database URL
    schema_file = f'{dataset_dir}/data_type_mappings.json'  # JSON file with table definitions

    # Extract data
    data_extractor = DataExtractor(dataset, dataset_dir)
    data_extractor.download_data()

    # Create loader instance
    loader = Loader(None, db_url, schema_file)

    # Create table first
    loader.create_table('sales')

    # Load and insert data from each file
    for file_path in file_paths:
        loader.file_path = file_path
        sales_data = loader.load_data()
        if sales_data is not None:
            loader.insert_data(sales_data, 'sales')
        else:
            logger.error(f"No data to insert from {file_path}")

if __name__ == "__main__":
    main_etl_function()
```

### 4. `data_type_mappings.json`

Defines the data type mappings for the columns in the PostgreSQL table.

```json
{
  "sales": {
    "timestamp": "String",
    "visitorid": "Integer",
    "event": "String",
    "itemid": "Integer",
    "transactionid": "Integer"
  }
}
```

### 5. `logs/` and `plugins/`

Directories for Airflow logs and plugins.

## Troubleshooting

### Check Docker Container Logs

If you encounter issues, check the logs for detailed error messages:

```bash
docker-compose logs CONTAINER_ID_FOR_WEBSERVER | grep head 5
docker-compose logs CONTAINER_ID_FOR_SCHEDULER | grep head 5
```

### Verify Environment Variable

Ensure the `AIRFLOW_PROJ_DIR` environment variable is set correctly:

```bash
echo $AIRFLOW_PROJ_DIR
```

### Verify Directory Structure Inside the Container

Enter the Airflow webserver container and check the contents of the directories:

```bash
docker-compose exec -it CONTAINER_ID_FOR_WEBSERVER /bin/bash
ls /opt/airflow/etl/vehicle_data/config
```

## License
