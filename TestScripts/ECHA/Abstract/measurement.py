# measurement.py
from config_loaders.measurement_config_loader import MeasurementConfigLoader

class Measurement:
    def __init__(self, config_loader: MeasurementConfigLoader):
        self.config_loader = config_loader

    def perform_measurement(self):
        high_priority_condition = self.config_loader.get_high_priority_condition()
        print(f"Performing measurement with condition: {high_priority_condition}")
        # 測定ロジックをここに実装
        result = {
            "isDone": 2,
            "n_mount": 2,
            "scan_height": 300.,
            "scan_width": 500.,
        }
        self.config_loader.register_experiment_result(result)
        print(f"Registered result: {result}")
        self.config_loader.outputCSV("output.csv")