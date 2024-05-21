# csv_measurement_config_loader.py
import csv
import sqlite3
from .measurement_config_loader import MeasurementConfigLoader

class CSVMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.db_file_path = 'config.db'
        self.load_config()

    def load_config(self):
        print("SQliteの登録そした体")

    def get_high_priority_condition(self):
        return 123

    def register_experiment_result(self, result):
        # resultはJSON形式
        print("Inserting result info to SQLITE")
        print(result)

        return True
