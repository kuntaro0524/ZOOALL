import requests
import csv
from abc import ABC, abstractmethod

class MeasurementConfigLoader(ABC):
    @abstractmethod
    def load_config(self):
        pass

class CSVMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def load_config(self):
        config = []
        with open(self.csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                config.append(row)
        return config

class APIMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, api_url):
        self.api_url = api_url

    def load_config(self):
        response = requests.get(self.api_url)
        response.raise_for_status()
        return response.json()

class Measurement:
    def __init__(self, config_loader: MeasurementConfigLoader):
        self.config_loader = config_loader
        self.config = self.config_loader.load_config()

    def perform_measurement(self):
        # 測定ロジックをここに実装
        for condition in self.config:
            print(f"Performing measurement with condition: {condition}")

if __name__ == "__main__":
    isCSV = True
    if isCSV:
        conds_loader = CSVMeasurementConfigLoader('config.csv')
    else:
        conds_loader = APIMeasurementConfigLoader('https://example.com/api/config')

    measurement = Measurement(conds_loader)
    measurement.perform_measurement()
