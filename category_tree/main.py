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
    FILE_PATH = 'ecommerce_data/category_tree.csv'
    SCHEMA_PATH = "category_tree/config/data_type_mappings.json"

    # extract data (Only run 2 lines below once)
    # extractor = Extractor(dataset=DATASET, dataset_dir=DIR)
    # extractor.get_data()

    # load and insert data into postgresql
    loader = Loader(file_path=FILE_PATH, table_name='category_trees', unit_dt=None, schema_path=SCHEMA_PATH)
    events = loader.load_data()
    if events is not None:
        loader.initialize_pg_table()
        loader.insert_data_to_pg()
    else:
        print(f"No data inserted into PostgreSQL")