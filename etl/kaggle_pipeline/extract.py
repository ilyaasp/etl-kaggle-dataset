import kaggle
import os
import zipfile
from loguru import logger

class Extractor:
    def __init__(self, dataset, dataset_dir) -> None:
        self.dataset = dataset
        self.dataset_dir = dataset_dir

    def get_data(self):
        """
        This function will create the directory directly inside the main directory
        Then, it will download the data
        And then, it will extract the dataset, if it's zipped
        Then, it will delete the zip file
        """
        try:
            # download the dataset
            kaggle.api.dataset_download_files(self.dataset, path=self.dataset_dir, unzip=True)

            # Check if the dataset is downloaded as a zip file or directly extracted
            zip_path = f"{self.dataset_dir}/{self.dataset.split('/')[-1]}.zip"

            if os.path.exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.dataset_dir)
                logger.info("Dataset downloaded and extracted from zip file.")
            else:
                logger.info("Dataset downloaded and extracted directly.")

            logger.info("Dataset downloaded and extracted successfully.")

        except Exception as e:
            logger.error(f"Error downloading or extracting dataset: {e}")
        