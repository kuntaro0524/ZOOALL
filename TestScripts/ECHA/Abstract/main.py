# main.py
from config_loaders.csv_measurement_config_loader import CSVMeasurementConfigLoader
from config_loaders.api_measurement_config_loader import APIMeasurementConfigLoader
from measurement import Measurement

if __name__ == '__main__':
    import sys
    switch = sys.argv[1]
    # URL
    api_url = "https://dcha-spx.spring8.or.jp/api1.0.2/"
    # CSVファイルを使用する場合
    if switch == 'csv':
        csv_loader = CSVMeasurementConfigLoader(sys.argv[2])
        measurement_csv = Measurement(csv_loader)
        measurement_csv.perform_measurement()
    elif switch == 'api':
        # Web APIを使用する場合
        zoo_id = 2
        api_loader = APIMeasurementConfigLoader(zoo_id)
        measurement_api = Measurement(api_loader)
        print("SDFSDFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
        measurement_api.perform_measurement()