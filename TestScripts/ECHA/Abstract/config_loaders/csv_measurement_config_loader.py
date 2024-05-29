# csv_measurement_config_loader.py
import csv
import os,sys
import sqlite3
import datetime
from .measurement_config_loader import MeasurementConfigLoader
import ESA

class CSVMeasurementConfigLoader(MeasurementConfigLoader):
    def __init__(self, csv_file_path):
        self.csv_file_path = os.path.abspath(csv_file_path)
        # root_path : self.csv_file_path のディレクトリ
        self.root_path = self.csv_file_path[:self.csv_file_path.rfind('/')]
        self.load_config()
        self.current_oindex = None

    def load_config(self):
        # DB fileが存在しないかを確認して、存在しない場合は作成する
        # dbfileのパスは、self.root_path
        # dbfileの名前に日付情報をいれる
        ttime = datetime.datetime.now()
        timestr=datetime.datetime.strftime(ttime, '%y%m%d%H%M%S')
        self.dbfilename = os.path.join(self.root_path, "zoo_%s.db"%timestr)

        # ESA
        self.esa = ESA.ESA(self.dbfilename)
        print("reading CSV file", self.csv_file_path)
        self.esa.makeTable(self.csv_file_path, force_to_make = True)
        print("DB OKAY")
        return True

    def get_high_priority_condition(self):
        cond = self.esa.getPriorPinCond()
        print("High priority condition is ", cond)
        # Current 'o_index' is saved.
        self.current_oindex = cond['o_index']
        return cond

    def register_experiment_result(self, result):
        # resultはJSON形式
        # 変数名：数値　の組なので順にDBに登録する
        print("Registering result to DB")
        for key, value in result.items():
            print("KEY: ", key, "VALUE: ", value)
            self.esa.updateValueAt(self.current_oindex, key, value)
        return True

    def outputCSV(self, csvfilename):
        df = self.esa.getDataFrame()
        df.to_csv(csvfilename, index=False)

        return True