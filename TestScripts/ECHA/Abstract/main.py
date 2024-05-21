# main.py
from config_loaders.csv_measurement_config_loader import CSVMeasurementConfigLoader
from config_loaders.api_measurement_config_loader import APIMeasurementConfigLoader
from measurement import Measurement

# CSVファイルを使用する場合
# import sys
# csv_loader = CSVMeasurementConfigLoader(sys.argv[1])
# measurement_csv = Measurement(csv_loader)
# measurement_csv.perform_measurement()

# Web APIを使用する場合
api_loader = APIMeasurementConfigLoader('https://example.com/api')
measurement_api = Measurement(api_loader)
measurement_api.perform_measurement()
