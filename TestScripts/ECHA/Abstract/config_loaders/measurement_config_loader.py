from abc import ABC, abstractmethod
import sqlite3
import requests

class MeasurementConfigLoader(ABC):
    @abstractmethod
    def load_config(self):
        pass

    @abstractmethod
    def get_high_priority_condition(self):
        pass

    @abstractmethod
    def register_experiment_result(self, result):
        pass
