
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
│   │   │   └── data_type_mappings.json
│   │   └── main.py
│   │
│   └── kaggle_pipeline/
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
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

# Basic Airflow cluster configuration for CeleryExecutor with Redis and PostgreSQL.
#
# WARNING: This configuration is for local development. Do not use it in a production deployment.
#
# This configuration supports basic configuration using environment variables or an .env file
# The following variables are supported:
#
# AIRFLOW_IMAGE_NAME           - Docker image name used to run Airflow.
#                                Default: apache/airflow:2.6.1
# AIRFLOW_UID                  - User ID in Airflow containers
#                                Default: 50000
# AIRFLOW_PROJ_DIR             - Base path to which all the files will be volumed.
#                                Default: .
# Those configurations are useful mostly in case of standalone testing/running Airflow in test/try-out mode
#
# _AIRFLOW_WWW_USER_USERNAME   - Username for the administrator account (if requested).
#                                Default: airflow
# _AIRFLOW_WWW_USER_PASSWORD   - Password for the administrator account (if requested).
#                                Default: airflow
# _PIP_ADDITIONAL_REQUIREMENTS - Additional PIP requirements to add when starting all containers.
#                                Use this option ONLY for quick checks. Installing requirements at container
#                                startup is done EVERY TIME the service is started.
#                                A better way is to build a custom image or extend the official image
#                                as described in https://airflow.apache.org/docs/docker-stack/build.html.
#                                Default: ''
#
# Feel free to modify this file to suit your needs.
---
version: '3.8'
x-airflow-common:
  &airflow-common
  # In order to add custom dependencies or upgrade provider packages you can use your extended image.
  # Comment the image line, place your Dockerfile in the directory where you placed the docker-compose.yaml
  # and uncomment the "build" line below, Then run `docker-compose build` to build the images.
  # image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.6.1}
  build: .
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    # For backward compatibility, with Airflow <2.3
    AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'true'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'
    # yamllint disable rule:line-length
    # Use simple http server on scheduler for health checks
    # See https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/check-health.html#scheduler-health-check-server
    # yamllint enable rule:line-length
    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'
    # WARNING: Use _PIP_ADDITIONAL_REQUIREMENTS option ONLY for a quick checks
    # for other purpose (development, test and especially production usage) build/extend Airflow image.
    _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:-}
    # proj dir
    # AIRFLOW_PROJ_DIR: /Users/ipman/Work/sales_data
    # HOME: /Users/ipman
  volumes:
    - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
    - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
    - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
    - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
    - ${AIRFLOW_PROJ_DIR:-.}/etl:/opt/airflow/etl
    - ${HOME:-.}/.kaggle:/home/airflow/.kaggle
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always

  redis:
    image: redis:latest
    expose:
      - 6379
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 30s
      retries: 50
      start_period: 30s
    restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8974/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-worker:
    <<: *airflow-common
    command: celery worker
    healthcheck:
      test:
        - "CMD-SHELL"
        - 'celery --app airflow.executors.celery_executor.app inspect ping -d "celery@$${HOSTNAME}"'
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    environment:
      <<: *airflow-common-env
      # Required to handle warm shutdown of the celery workers properly
      # See https://airflow.apache.org/docs/docker-stack/entrypoint.html#signal-propagation
      DUMB_INIT_SETSID: "0"
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-triggerer:
    <<: *airflow-common
    command: triggerer
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type TriggererJob --hostname "$${HOSTNAME}"']
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    # yamllint disable rule:line-length
    command:
      - -c
      - |
        function ver() {
          printf "%04d%04d%04d%04d" $${1//./ }
        }
        airflow_version=$$(AIRFLOW__LOGGING__LOGGING_LEVEL=INFO && gosu airflow airflow version)
        airflow_version_comparable=$$(ver $${airflow_version})
        min_airflow_version=2.2.0
        min_airflow_version_comparable=$$(ver $${min_airflow_version})
        if (( airflow_version_comparable < min_airflow_version_comparable )); then
          echo
          echo -e "\033[1;31mERROR!!!: Too old Airflow version $${airflow_version}!\e[0m"
          echo "The minimum Airflow version supported: $${min_airflow_version}. Only use this or higher!"
          echo
          exit 1
        fi
        if [[ -z "${AIRFLOW_UID}" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: AIRFLOW_UID not set!\e[0m"
          echo "If you are on Linux, you SHOULD follow the instructions below to set "
          echo "AIRFLOW_UID environment variable, otherwise files will be owned by root."
          echo "For other operating systems you can get rid of the warning with manually created .env file:"
          echo "    See: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#setting-the-right-airflow-user"
          echo
        fi
        one_meg=1048576
        mem_available=$$(($$(getconf _PHYS_PAGES) * $$(getconf PAGE_SIZE) / one_meg))
        cpus_available=$$(grep -cE 'cpu[0-9]+' /proc/stat)
        disk_available=$$(df / | tail -1 | awk '{print $$4}')
        warning_resources="false"
        if (( mem_available < 4000 )) ; then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough memory available for Docker.\e[0m"
          echo "At least 4GB of memory required. You have $$(numfmt --to iec $$((mem_available * one_meg)))"
          echo
          warning_resources="true"
        fi
        if (( cpus_available < 2 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough CPUS available for Docker.\e[0m"
          echo "At least 2 CPUs recommended. You have $${cpus_available}"
          echo
          warning_resources="true"
        fi
        if (( disk_available < one_meg * 10 )); then
          echo
          echo -e "\033[1;33mWARNING!!!: Not enough Disk space available for Docker.\e[0m"
          echo "At least 10 GBs recommended. You have $$(numfmt --to iec $$((disk_available * 1024 )))"
          echo
          warning_resources="true"
        fi
        if [[ $${warning_resources} == "true" ]]; then
          echo
          echo -e "\033[1;33mWARNING!!!: You have not enough resources to run Airflow (see above)!\e[0m"
          echo "Please follow the instructions to increase amount of resources available:"
          echo "   https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#before-you-begin"
          echo
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "${AIRFLOW_UID}:0" /sources/{logs,dags,plugins}
        exec /entrypoint airflow version
    # yamllint enable rule:line-length
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_UPGRADE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
      _PIP_ADDITIONAL_REQUIREMENTS: ''
    user: "0:0"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/sources

  airflow-cli:
    <<: *airflow-common
    profiles:
      - debug
    environment:
      <<: *airflow-common-env
      CONNECTION_CHECK_MAX_COUNT: "0"
    # Workaround for entrypoint issue. See: https://github.com/apache/airflow/issues/16252
    command:
      - bash
      - -c
      - airflow

  # You can enable flower by adding "--profile flower" option e.g. docker-compose --profile flower up
  # or by explicitly targeted on the command line e.g. docker-compose up flower.
  # See: https://docs.docker.com/compose/profiles/
  flower:
    <<: *airflow-common
    command: celery flower
    profiles:
      - flower
    ports:
      - "5555:5555"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:5555/"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

volumes:
  postgres-db-volume:
```

### 2. `events_dag.py`

Contains the Airflow DAG that defines the ETL process for a specific ETL or a group of ETLs.

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

def_args = {
    'owner': 'ilyas',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'vehicle_data_etl_DAG',
    default_args=def_args,
    description='ETL of events table',
    schedule_interval=timedelta(days=1),
)

run_etl_task = BashOperator(
    task_id='run_events_etl',
    bash_command="cd /opt/airflow/etl/vehicle_data && python3 main.py",
    dag=dag,
)

run_etl_task
```

### 3. `main.py`

Contains the main ETL logic, including extracting data, transforming it, and loading it into PostgreSQL.

```python
import sys
import os
from loguru import logger

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaggle_pipeline.load import Loader
from kaggle_pipeline.extract import Extractor

def main_etl():
    """
    Define the following parameters:
    file_path
    dataset
    dataset_dir
    file_path
    """
    # parameters
    DATASET = 'syedanwarafridi/vehicle-sales-data' # 'retailrocket/ecommerce-dataset'
    DIR = 'vehicle_data_sales'
    FILE_PATH = '/opt/airflow/etl/vehicle_data/vehicle_data_sales/car_prices.csv'
    SCHEMA_PATH = "/opt/airflow/etl/vehicle_data/config/data_type_mappings.json" # /opt/airflow/etl/vehicle_data

    # extract data (Only run 2 lines below once)
    extractor = Extractor(dataset=DATASET, dataset_dir=DIR)
    extractor.get_data()

    # load and insert data into postgresql
    loader = Loader(file_path=FILE_PATH, table_name='vehicle_sales', unit_dt='ms', schema_path=SCHEMA_PATH)
    events = loader.load_data()
    if events is not None:
        loader.initialize_pg_table()
        loader.insert_data_to_pg()
    else:
        print(f"No data inserted into PostgreSQL")

if __name__ == "__main__":
    main_etl()
```

### 4. `data_type_mappings.json`

Defines the data type mappings for the columns in the PostgreSQL table. This is with the same directory with main.py that's below config directory

```json
{
    "year": "int",
    "make": "str",
    "model": "str",
    "trim": "str",
    "body": "str",
    "transmission": "str",
    "vin": "str",
    "state": "str",
    "condition": "int",
    "odometer": "int",
    "color": "str",
    "interior": "str",
    "seller": "str",
    "mmr": "int",
    "sellingprice": "int",
    "saledate": "datetime"
}
```

### 5. `Kaglle Pipeline`

There are four files here. `extract.py`, `transform.py`, `load.py` and `utils.py`. These four files act as reusable modules for etls that can be created within etl directories (eg: vehicle_data)

```json
{
    "year": "int",
    "make": "str",
    "model": "str",
    "trim": "str",
    "body": "str",
    "transmission": "str",
    "vin": "str",
    "state": "str",
    "condition": "int",
    "odometer": "int",
    "color": "str",
    "interior": "str",
    "seller": "str",
    "mmr": "int",
    "sellingprice": "int",
    "saledate": "datetime"
}
```

### 6. `logs/` and `plugins/`

Directories for Airflow logs and plugins.

## Troubleshooting

### Check Docker Container Logs for Debugging

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
