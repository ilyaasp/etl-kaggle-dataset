import sys
import os
from loguru import logger

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaggle_pipeline.load import Loader
from kaggle_pipeline.extract import Extractor

if __name__ == "__main__":
    """
    Define the following parameters:
    file_path
    dataset
    dataset_dir
    file_path
    """
    # parameters
    DATASET = 'retailrocket/ecommerce-dataset'
    DIR = 'ecommerce_data'
    FILE_PATH = ['ecommerce_data/item_properties_part1.csv', 'ecommerce_data/item_properties_part2.csv']
    SCHEMA_PATH = "item_properties/config/data_type_mappings.json"

    # extract data (Only run 2 lines below once)
    # extractor = Extractor(dataset=DATASET, dataset_dir=DIR)
    # extractor.get_data()

    # load and insert data into postgresql
    for file_path in FILE_PATH:
        loader = Loader(file_path=file_path, table_name='item_properties', unit_dt='ms', schema_path=SCHEMA_PATH)
        events = loader.load_data()
        if events is not None:
            loader.initialize_pg_table()
            loader.insert_data_to_pg(is_replace=False)
        else:
            print(f"No data inserted into PostgreSQL")