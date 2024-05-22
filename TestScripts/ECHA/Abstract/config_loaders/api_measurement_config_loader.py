# api_measurement_config_loader.py
import requests
from .measurement_config_loader import MeasurementConfigLoader
from .ESAloaderAPI import ESAloaderAPI

class APIMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, zoo_id):
        self.esa_loader = ESAloaderAPI(zoo_id)
        self.isRead = False

    def load_config(self):
        # ここで条件リストを読み出して、self.conditionsに格納する
        print("@@@@@@@@@@@@@@@@@@@@@@ LADING")
        self.conditions = self.esa_loader.getCondDataFrame()
        self.isRead = True
        pass

    def getCurentMeasureID(self):
        return self.measure_id

    def get_high_priority_condition(self):
        if self.isRead == False:
            self.load_config()

        print("######################<<<<<<<<<<<<<<<<<<<<<")
        # self.conditions (pandas.DataFrame)を p_index でソートして、最初の行を取得
        # ここで条件の取得方法を変更する
        high_priority_condition = self.conditions.sort_values(by='p_index').iloc[0]
        print(high_priority_condition)
        # measureIDを保持する
        self.measure_id = high_priority_condition['measure_id']

        return high_priority_condition

    def register_experiment_result(self, result):
        # result は　dict型　で、測定結果を表す 
        for key, value in result.items():
            print(key, value)
            self.esa_loader.putCond(self.measure_id, key, value)

        print("Registering experiment result")
        print("MeasureID is " + str(self.measure_id))

        return True

    def outputCSV(self, csvfilename):
        self.conditions.to_csv(csvfilename, index=False)
        return True