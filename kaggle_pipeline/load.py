import sys
import os
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.types import Integer, Float, String, Boolean, DateTime

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kaggle_pipeline.transform import Transformer

class Loader:
    def __init__(self, file_path, table_name, unit_dt, schema_path,
                 db_url='postgresql://admin:password@localhost:5432/sales_data') -> None:
        self.file_path = file_path
        self.metadata = MetaData()
        self.table_name = table_name
        self.unit_dt = unit_dt
        self.schema_path = schema_path
        self.transformer = Transformer(schema_path=schema_path)
        self.engine = create_engine(db_url)

    def load_data(self):
        try:
            # check if file exists
            if not os.path.exists(self.file_path):
                logger.error(f"File not found: {self.file_path}")
                return None
            
            # load data
            df = pd.read_csv(self.file_path)
            logger.info(f"Data loaded successfully from {self.file_path}")
            return df
        
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
        
    def initialize_pg_table(self):
        """
        Define table with appropriate data type
        """
        try:
            columns = [Column(column_name, self.get_sqlalchemy_type(data_type))
                       for column_name, data_type in self.transformer.data_type_mappings.items()]
            table = Table(self.table_name, self.metadata, *columns)

            # Create the table if it doesn't exist
            self.metadata.create_all(self.engine)
            logger.info(f"Table {self.table_name} created successfully.")

        except Exception as e:
            logger.error(f"Error initializing table {e}")

    def insert_data_to_pg(self, is_replace=None):
        """
        Insert data from csv to Postgresql
        """
        try:
            df = self.load_data()
            df = self.transformer.transform_data_type(df, unit_dt=self.unit_dt)
            if df is None:
                logger.error(f"Data transformation failed")
                return
            
            # Insert data into the table
            if is_replace or is_replace is None:
                df.to_sql(self.table_name, self.engine, if_exists='replace', index=False)
            else:
                df.to_sql(self.table_name, self.engine, if_exists='append', index=False)

            logger.info("Data inserted successfully into PostgreSQL")
            
        except Exception as e:
            logger.error(f"Error inserting data into PostgreSQL {e}")

    def get_sqlalchemy_type(self, data_type):
        """
        Assign appropriate sql alchemy data type as per data_type_mappings.json
        """
        if data_type == "str":
            return String
        elif data_type == "int":
            return Integer
        elif data_type == "float":
            return Float
        elif data_type == "boolean":
            return Boolean
        elif data_type == "datetime":
            return DateTime
        else:
            logger.error(f"Unsupported data type {data_type}")
            return None
        
    