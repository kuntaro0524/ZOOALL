# api_measurement_config_loader.py
import requests
from .measurement_config_loader import MeasurementConfigLoader

class APIMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, api_url):
        self.api_url = api_url

    def load_config(self):
        # Web APIの場合、load_configメソッドは特に処理を行わない
        pass

    def get_high_priority_condition(self):
        return 245

    def register_experiment_result(self, result):
        print("Inserting result info to API")
        print(result)
        return True
