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
    FILE_PATH = 'vehicle_data_sales/car_prices.csv'
    SCHEMA_PATH = "/etl/config/data_type_mappings.json" # /opt/airflow/etl/vehicle_data

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