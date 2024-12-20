from typing import Any
import requests
from datetime import datetime, timedelta
# 設定値
import pandas as pd
import json
import logging

class ESAloaderAPI:
    def __init__(self, zoo_id):
        self.api_url = "https://dcha-spx.spring8.or.jp/api1.0.2/"
        self.login_url = "%sdj-rest-auth/login/"%self.api_url
        #self.data_request_url = "%szoo_measure/"%self.api_url
        self.data_request_url = "%szoo_samplepin/"%self.api_url
        self.measure_data_url = "%sparameter_measure/"%self.api_url
        self.params_data_url = "%sparameter/"%self.api_url
        self.username = "admin"
        self.password = "000nimda"
        self.token_expiry = None
        self.access_token = None
        self.zoo_id = zoo_id

        # Flag in steps
        self.isLogin = False
        self.isExpired = False
        self.isPrepParams = False
        self.isPrepConds = False # get condition list from DB 

        # logger 
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
        # log file 
        log_file = 'esa_loader.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def get_access_token(self):
        print(self.login_url,self.username, self.password)
        response = requests.post(self.login_url, data={"username": self.username, "password": self.password})
        if response.status_code == 200:
            token_data = response.json()
            print("####################")
            print(token_data)
            print("####################")
            self.access_token = token_data['access_token']
            # トークンが作成された時刻は 'last_login' に格納されている
            # この時間に１時間を足した時間がトークンの有効期限
            # format '2024-04-25T07:21:34.153331+09:00'
            last_login = datetime.strptime(token_data['user']['last_login'], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.token_expiry = last_login + timedelta(hours=1)
            # Time zone が付いているので、取り除く
            self.token_expiry = self.token_expiry.replace(tzinfo=None)
            self.isLogin = True
            print("Logged in!")
        else:
            print("Exception!!!!!!!!!!!")
            raise Exception("Failed to login")

    def getCondDataFrame_obsoleted(self):
        self.logger.info("getCondDataFrame starts")
        self.logger.info(f"Data request URL: {self.data_request_url}")
        self.logger.info(f"ZOOID: {self.zoo_id}")
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.data_request_url, headers=auth_headers, params={"zoo_id":self.zoo_id})
        self.logger.info(f"Response: {response}")
        # response を pandas DataFrame に変換
        df = pd.DataFrame(response.json())
        # df の１行ずつのデータ取得
        # この辞書をリストに追加していく
        data_list = []
        for i in range(len(df)):
            # 'zoo_samplepin_id' を取得
            zoo_samplepin_id=df.iloc[i]['id']
            print(f"zoo sample pin id: {zoo_samplepin_id}")
            # parameterを取得する
            target_url = f"{self.api_url}/zoo_parameter_samplepin/"
            response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id":zoo_samplepin_id})
            # print(response.json())
            each_df = pd.DataFrame(response.json())
            # print(each_df.columns)
            dicts = {}
            for j in range(len(each_df)):
            # この each_df に含まれている１行のデータの 'parameter_name' と 'value' で dictionaryを作成
                dicts[each_df.iloc[j]['parameter_name']] = each_df.iloc[j]['value']
                # measure_idを追加する
                dicts['zoo_samplepin_id'] = zoo_samplepin_id

            # dicts を Series に変換
            each_pin_df = pd.Series(dicts)
            # print(each_pin_df)
            data_list.append(each_pin_df)

        # data_list からpandas DataFrameを作成
        self.conds_df = pd.DataFrame(data_list)
        self.isPrepConds = True

        return self.conds_df

    # coded by K. Hirata 2024/12/16
    def getCondDataFrame(self):
        self.logger.info("getCondDataFrame starts")
        self.logger.info(f"Data request URL: {self.data_request_url}")
        self.logger.info(f"ZOOID: {self.zoo_id}")
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.data_request_url, headers=auth_headers, params={"zoo_id":self.zoo_id})
        # response を pandas DataFrame に変換
        df = pd.DataFrame(response.json())
        # df の１行ずつのデータ取得
        # この辞書をリストに追加していく
        data_list = []
        for i in range(len(df)):
            # 'zoo_samplepin_id' を取得
            zoo_samplepin_id=df.iloc[i]['id']
            self.logger.info(f"zoo sample pin id: {zoo_samplepin_id}")
            # parameter を取得する
            # APIのメソッドを利用する
            # zoo_parameter_samplepin/get_list/
            target_url = f"{self.api_url}/zoo_parameter_samplepin/get_list/"
            # params: {"zoo_samplepin_id":zoo_samplepin_id}
            response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id":zoo_samplepin_id})
            # json を dictにして保存
            # 最終的にはリストに追加してDataFrameに変換する
            tmp_dict = response.json()
            data_list.append(tmp_dict)

        # DataFrame に変換
        self.conds_df = pd.DataFrame(data_list)
        return self.conds_df
        # end of getCondDataFrame2

    def make_authenticated_request(self):
        # すでにログインしている場合には、トークンの有効期限を確認する
        if self.isLogin == False:
            self.get_access_token()
            self.auth_headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
        else:
            # 現在の時刻
            currtime = datetime.now()
            if self.token_expiry is None or datetime.now() >= self.token_expiry:
                self.get_access_token()
                self.auth_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
        return self.auth_headers

    def test(self):
        if self.isLogin == False:
        # トークンの有効期限が切れているか確認
            if self.token_expiry is None or datetime.now() >= self.token_expiry:
                print("Token is expired")
                self.get_access_token()  # トークンが切れていたら新しく取得
                self.auth_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
            else:
                print("Token is still valid")

    def putCond(self, measure_id, parameter_name, value):
        print(f"putCond!!!! {measure_id}, {parameter_name}, {value}")
        # convert 'parameter_name' to 'parameter_id'
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/parameter_measure/"
        # parameter_id 
        parameter_id = self.convParamname2Paramid(parameter_name)
        print("parameter_name: ", parameter_name)
        print("parameter_id: ", parameter_id, " thats") 
        data = {"measure_id":measure_id, "parameter_id":parameter_id, "value":value}
        response = requests.post(target_url, headers=auth_headers, data={"measure_id":measure_id, "parameter_id":parameter_id, "value":value})
        # response = requests.put(target_url, headers=auth_headers, data={"measure_id":measure_id, "parameter_id":parameter_id, "value":value})
        print(response.json())
        print("putCond is done")

    def updateCond(self, measure_id, parameter_name, value):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/parameter_measure/update_multiple_data/"

        # JSON リストを作成する
        data = [{"measure_id":measure_id, "parameter_name":parameter_name, "value":value}]
        # JSONへ変換
        # data = json.dumps(data)
        response = requests.post(target_url, headers=auth_headers, json=data)
        print(response.json())
        print("updated!!")

    def updateConds(self, json_data):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/parameter_measure/update_multiple_data/"
        response = requests.post(target_url, headers=auth_headers, json=json_data)
        print(response.json())
        print("updated!!")

    def convParamname2Paramid(self, parameter_name):
        # パラメータのリストを取得する
        if self.isPrepParams == False:
            self.getParameterList()

        print(self.paramtable_df)
        # paramtable_df から 'parameter_name' に対応する 'parameter_id' を取得
        # 例えば、'parameter_name' が 'isDone' の場合、'parameter_id' は 
        # 1 になる
        tmp_id = self.paramtable_df[self.paramtable_df['parameter_name'] == parameter_name]['id']
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        print(tmp_id)
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        param_id = self.paramtable_df[self.paramtable_df['parameter_name'] == parameter_name]['id'].values[0]

        return param_id

    def getParameterList(self):
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.params_data_url, headers=auth_headers)
        json_data = response.json()
        self.paramtable_df = pd.DataFrame(json_data)
        self.isPrepParams=True
        csv_file_path = 'received_params.csv'
        self.paramtable_df.to_csv(csv_file_path)

    # zoo_id が 指定されたものの条件について新しく実験中用のパラメータを追加する
    def addZOOparams(self):
        # zoo_idが指定したもののmeasure_idを取得する
        if self.isPrepConds == False:
            self.getCondDataFrame()

        # 追加するパラメータについては以下の通り
        # ゆくゆくは config fileで記述するようにしたい
        initial_params = {
            'isDone' : 0,
            'isSkip' : 0,
            'isMount' : 0,
            'isLoopCenter' : 0,
            'isRaster' : 0,
            # 'isDS' : 0,
            'scan_height' : 0.0,
            'scan_width' : 0.0,
            'n_mount' : 0,
            'nds_multi' : 0,
            'nds_herical' : 0,
            'nds_helpart' : 0,
            't_meas_start' : "0",
            't_mount_end' : "",
            't_cent_start' : "0",
            't_cent_end' : "0",
            't_raster_start' : "0",
            # 't_raster_end' : "0",
            't_ds_start' : "0",
            't_ds_end' : "0",
            't_dismount_start' : "0",
            't_dismount_end' : "0",
            'data_index' : 0,
            'n_mount_fails' : 0,
            'log_mount' : "0",
            'hel_cry_size' : 0.0,
            'flux' : 0.0,
            'phs_per_deg' : 0.0
        }

        starttime = datetime.now()
        # self.cond_dfに含まれているmeasure_idに対して、上記のパラメータを追加する
        for measure_id in self.conds_df['measure_id']:
            print(measure_id)
            for key in initial_params.keys():
                print("###############################")
                print("LOOPG: ", key, initial_params[key])
                self.putCond(measure_id, key, initial_params[key])
        endtime = datetime.now()
        # consumed time
        consumed_time = endtime - starttime
        print("Consumed Time: ", consumed_time)

# もしもmainが定義されていない場合以下を実行
if __name__ == '__main__':
    # class をインスタンス化
    zoo_id = 6
    esa_loader = ESAloaderAPI(zoo_id)
    # ログイン
    esa_loader.make_authenticated_request()
    
    # データを取得する関数を使用
    start_time = datetime.now()
    esa_loader.getParameterList()
    
    # 条件を新たに追加したらどうなるか？
    # esa_loader.addZOOparams()
    # end_time = datetime.now()
    
    # # 消費時間を計算 (sec)
    # consumed_time = end_time - start_time
    # print("Consumed Time: ", consumed_time)
    #conds_df = esa_loader.getCondDataFrame()
    conds_df = esa_loader.getCondDataFrame()
    print(conds_df)
    #conds_df.to_csv("test.csv")
    # csv_file_path = 'received_mod2.csv'
    # conds_df.to_csv(csv_file_path)
    # esa_loader.addZOOparams()
    #esa_loader.updateCond(21520, "isDone", "12")
    # esa_loader.putCond(21520, "isDone", 1)
    # conds_df = esa_loader.getCondDataFrame()
    # csv_file_path = 'pppp.csv'
    # conds_df.to_csv(csv_file_path)