FROM apache/airflow:2.9.2
ADD requirements.txt .
RUN pip install -r requirements.txt