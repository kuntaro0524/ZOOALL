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
        #self.username = "admin"
        #self.password = "000nimda"
        self.username = "operator"
        self.password = "1tk2p3640"
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

    def isSkipped(self, zoo_samplepin_id):
        start_time = datetime.now()
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/"
        print(f"target_url: {target_url}")
        response = requests.get(target_url, headers=auth_headers,params={"zoo_id":self.zoo_id})
        json_data = response.json()
        # zoo_samplepin_id に対応するデータを取得
        for data in json_data:
            if data['id'] == zoo_samplepin_id:
                # data['isSkip'] が 1 ならばTrue そうでないならばFalse
                end_time = datetime.now()
                consumed_time = end_time - start_time
                print(f"Consumed Time: {consumed_time}")
                return data['isSkip'] == 1

    def getCond(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_parameter_samplepin/get_list/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id":zoo_samplepin_id})
        # dictionary に変換
        cond_dict = response.json()
        return cond_dict

    def getSamplePin(self):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_id":self.zoo_id})
        # この時点で取得したデータは以下が含まれている
        # id, exid, o_index, p_index, isSkip, 
        # isDone, created_at, updated_at, zoo_id
        # response を pandas DataFrame に変換
        df = pd.DataFrame(response.json())
        self.logger.info(f"Dataframe: {df}")

        return df

    # coded by K. Hirata 2024/12/16
    def getCondDataFrame(self):
        self.logger.info("getCondDataFrame starts")
        # zoo_samplepin の取得
        auth_headers = self.make_authenticated_request()

        # zoo_samplepin の取得
        df = self.getSamplePin(self.zoo_id)

        # 上記で取得した id -> zoo_samplepin_id を利用して
        # 各パラメータを辞書にする→最終的にDFに変換する
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

    # this was obsoleted in the current 'zoo_samplepin' version
    # 2025/02/12
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

    # 2025/02/12 coded
    def setDone(self, p_index, zoo_samplepin_id, isDone):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/{zoo_samplepin_id}/"
        print(f"target_url: {target_url}")
        params= {
            "isDone": isDone,
            "p_index": p_index
        }

        # params は data で渡す必要がある（三田さん情報）
        response = requests.put(target_url, headers=auth_headers, data=params)
        print(f"Raw response={response}")

        try:
            json_data = response.json()
            self.logger.info(f"Response: {json_data}")
            return True
        except requests.exceptions.JSONDecodeError:
            self.logger.info(f"Failed to setDone: {response.status_code}")
            return False

    def setSkip(self, p_index, zoo_samplepin_id, isSkip):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/{zoo_samplepin_id}/"
        self.logger.info(f"target_url: {target_url}")
        data_params = {
            "isSkip": isSkip,
            "p_index": p_index
        }
        response = requests.put(target_url, headers=auth_headers, data=data_params)
        self.logger.info(f"Raw response={response}")
        try:
            json_data = response.json()
            self.logger.info(f"Response: {json_data}")
            return True
        except requests.exceptions.JSONDecodeError:
            self.logger.info(f"Failed to setSkip: {response.status_code}")
            return False
        
    # post result 
    # param_jsonはJSON形式
    # パラメータのリストは以下のURL先にある
    # https://docs.google.com/spreadsheets/d/1FOFIqBsO4myY7BVIsj6hlMz3fsNlrLBrxmJaJw7bSkQ/edit?gid=2077362619#gid=2077362619
    def postResult(self, sample_pin_id, param_json):
        # target url 
        target_url = f"{self.api_url}/zoo_result_samplepin/"
        print(f"target_url: {target_url}")

        # param_jsonにsample_pin_id を追加する
        param_json['zoo_samplepin_id'] = sample_pin_id
        print(f"after: {param_json}")

        # put
        auth_headers = self.make_authenticated_request()
        response = requests.post(target_url, headers=auth_headers, json=param_json)
        #response = requests.post(target_url, headers=auth_headers, data=param_json)
        # 失敗したら例外を発生させる
        print(f"response: {response}")
        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"Failed to post result: {response.status_code}")
        print(response.json())
        print("posted!!")

        return True

    def getResult(self, sample_pin_id):
        target_url = f"{self.api_url}/zoo_result_samplepin/"
        auth_headers = self.make_authenticated_request()
        response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id":sample_pin_id})
        # 取得したJSONを辞書にする
        result_dict = response.json()
        # 結果について表示をする
        result_df = pd.DataFrame(result_dict)
        return result_df

    def getNextPin(self):
        auth_headers = self.make_authenticated_request()
        # URL for get the limited 
        target_url = f"{self.api_url}/zoo_samplepin/"

        # query parameters
        query_params = {
            "isDone":0,
            "isSkip":0,
            "limit":1,
            "zoo_id":self.zoo_id
        }

        # isDone=0 & isSkip=0 & p_index 
        response = requests.get(self.data_request_url, headers=auth_headers, params=query_params)
        results_json = response.json()['results']
        # dictionary 
        # results_json が空の場合
        if len(results_json) == 0:
            return None
        dict_results = results_json[0]
        # 'id' の名称を 'zoo_samplepin_id' に変更する
        dict_results['zoo_samplepin_id'] = dict_results.pop('id')

        return dict_results
        
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
            'nds_helical' : 0,
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
    zoo_id = 12
    esa_loader = ESAloaderAPI(zoo_id)
    # ログイン
    esa_loader.make_authenticated_request()
    
    # データを取得する関数を使用
    #start_time = datetime.now()
    #esa_loader.getParameterList()
    
    # 条件を新たに追加したらどうなるか？
    # esa_loader.addZOOparams()
    # end_time = datetime.now()
    
    # # 消費時間を計算 (sec)
    # consumed_time = end_time - start_time
    # print("Consumed Time: ", consumed_time)
    isDebug=True
    target_pin_id = 186
    p_index = 0
    isDone = 0

    if isDebug==True:
        conds_df = esa_loader.getCondDataFrame()
        print(conds_df)
        print(conds_df.columns)
        # columnsの型を表示
        print(conds_df.dtypes)

        # zoo_samplepin について結果を登録する
        esa_loader.setDone(p_index, target_pin_id, isDone=isDone)

    # 結果の登録
    # Result 登録の試験
    param_json ={
        "data": [
            {"isMount":1},
            {"isDS":1},
            {"scan_height":300.0},
            {"scan_width":300.6},
            {"n_mount":3},
            {"nds_multi":1},
            {"nds_helical":0},
            {"nds_helpart":0},
            {"data_index":1},
            {"n_mount_fails":0},
            {"hel_cry_size":0.0},
            {"flux":2.35E10},
            {"phs_per_deg":1.0E15},
            {"log_mount":"Mount started"},
            {"t_meas_start":"data collection started"},
            {"t_mount_end":"mounting a pin finished"},
            {"t_cent_start":"centering started"},
            {"t_cent_end":"centering finished"},
            {"t_raster_start":"raster scan started"},
            {"t_raster_end":"raster scan finished"},
            {"t_ds_start":"data collection started"},
            {"t_ds_end":"data collection finished"},
            {"t_dismount_start":"dismounting sample started"},
            {"t_dismount_end":"dismounting sample finished"}
        ]
    }
    """
    """
    esa_loader.postResult(target_pin_id, param_json)
    result_df = esa_loader.getResult(target_pin_id)

    print(f"Result: {result_df}")
    # result_df の絡むごとに変数型を表示
    print(result_df.dtypes)
    # coluns 'created_at' には　'2025-02-12T12:24:30.497808+09:00
    # という形式で格納されている時間がある
    # これをdatetime型に変換する
    result_df['created_at'] = pd.to_datetime(result_df['created_at'])
    print(result_df.dtypes)

    esa_loader.getNextPin()

    """
    # conds_df に登録されているものについて isDoneを設定する
    for i in range(len(conds_df)):
        # zoo_samplepin_id
        zoo_samplepin_id = conds_df.iloc[i]['zoo_samplepin_id']
        # p_index
        p_index = conds_df.iloc[i]['p_index']
        # isDone
        isDone = 1
        # 登録
        esa_loader.setDone(p_index, zoo_samplepin_id, isDone=isDone)
    """

"""

"""
    
    #conds_df.to_csv("test.csv")
    # csv_file_path = 'received_mod2.csv'
    # conds_df.to_csv(csv_file_path)
    # esa_loader.addZOOparams()
    #esa_loader.updateCond(21520, "isDone", "12")
    # esa_loader.putCond(21520, "isDone", 1)
    # conds_df = esa_loader.getCondDataFrame()
    # csv_file_path = 'pppp.csv'
    # conds_df.to_csv(csv_file_path)