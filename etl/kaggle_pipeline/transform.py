import sys
import os
import pandas as pd
from loguru import logger

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaggle_pipeline.utils import _read_json_file

class Transformer:
    def __init__(self, schema_path) -> None:
        self.schema_path = schema_path
        self.data_type_mappings = _read_json_file(self.schema_path)
        
    def transform_data_type(self, dataframe, unit_dt=None):
        try:
            # adjust data type
            for column, dtype in self.data_type_mappings.items():
                if dtype == "str":
                    dataframe[column] = dataframe[column].astype(str)
                elif dtype == "int":
                    dataframe[column] = dataframe[column].astype(int)
                elif dtype == "float":
                    dataframe[column] = dataframe[column].astype(float)
                elif dtype == "boolean":
                    dataframe[column] = dataframe[column].astype(bool)
                elif dtype == "datetime":
                    if unit_dt is not None:
                        dataframe[column] = pd.to_datetime(dataframe[column], unit=unit_dt)
                    else:
                        dataframe[column] = pd.to_datetime(dataframe[column])
                else:
                    logger.error(f"Unsupported data type {dtype} for column {column}")
                    return None

            logger.info("Data type transformation is successful.")
            return dataframe
        
        except Exception as e:
            logger.error(f"Error transforming data {e}")
            return None