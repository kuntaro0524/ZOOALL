from typing import Any
import requests
from datetime import datetime, timedelta
# 設定値
import pandas as pd
import json
import logging
import sys

class ESAloaderAPI:
    def __init__(self, exid):
        self.api_url = "https://dcha-spx.spring8.or.jp/api1.0.2/"
        self.login_url = "%sdj-rest-auth/login/"%self.api_url
        #self.data_request_url = "%szoo_measure/"%self.api_url
        self.data_request_url = "%szoo_samplepin/"%self.api_url
        self.measure_data_url = "%sparameter_measure/"%self.api_url
        # NOTE:
        # parameter_measure/ は measure_id, parameter_id, value を要求する別系統API。
        # 現在の result 登録は zoo_result_samplepin/create_multiple_data/ を使用する。
        self.params_data_url = "%sparameter/"%self.api_url
        self.operator_id = "operator"
        self.password = "1tk2p3640"
        self.username = None
        self.token_expiry = None
        self.access_token = None
        self.exid = exid

        # Flag in steps
        self.isLogin = False
        self.isExpired = False
        self.isPrepParams = False
        self.isPrepConds = False # get condition list from DB 

        # logger 
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            self.logger.addHandler(handler)

            log_file = 'esa_loader.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)

        self.isInit = False

    def prep(self):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo/"
        response = requests.get(target_url, headers=auth_headers, params={"exid": self.exid})

        zoo_list = response.json()
        self.logger.info(f"User info response: {zoo_list}")

        if not isinstance(zoo_list, list):
            raise ValueError(f"Unexpected response type for /zoo/: {type(zoo_list)}")

        if len(zoo_list) == 0:
            raise ValueError(f"No zoo record found for exid={self.exid}")

        if len(zoo_list) > 1:
            raise ValueError(f"Multiple zoo records found for exid={self.exid}")

        self.zoo_id = zoo_list[0]["id"]
        self.username = zoo_list[0]["username"]
        self.isInit = True

    def get_username(self):
        if self.isInit == False:
            self.prep()
        return self.username

    def get_access_token(self):
        self.logger.info(f"Attempting to login with username: {self.operator_id}")
        response = requests.post(
        self.login_url,
            data={"username": self.operator_id, "password": self.password}
        )
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            safe_info = {
                "user": token_data.get("user", {}),
                "has_access_token": "access_token" in token_data,
            }
            self.logger.info(f"Login successful. Token data: {safe_info}")
            # トークンが作成された時刻は 'last_login' に格納されている
            # この時間に１時間を足した時間がトークンの有効期限
            # format '2024-04-25T07:21:34.153331+09:00'
            last_login = datetime.strptime(token_data['user']['last_login'], "%Y-%m-%dT%H:%M:%S.%f%z")
            self.token_expiry = last_login + timedelta(hours=1)
            # Time zone が付いているので、取り除く
            self.token_expiry = self.token_expiry.replace(tzinfo=None)
            self.isLogin = True
            self.logger.info("Logged in!")
        else:
            self.logger.error(f"Failed to login: {response.status_code} - {response.text}")
            raise Exception("Failed to login")

    # zoo_samplepin_id がスキップされているかどうかを確認する
    def isSkipped(self, zoo_samplepin_id):
        start_time = datetime.now()
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/"
        self.logger.info(f"Target URL: {target_url}")

        response = requests.get(
            target_url,
            headers=auth_headers,
            params={"zoo_id": self.zoo_id}
        )

        # APIからのレスポンスが200でない場合はエラーとする
        if response.status_code != 200:
            self.logger.error(f"isSkipped failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get zoo_samplepin list: {response.status_code}")

        # レスポンスの内容を辞書に変換
        body = response.json()

        # zoo_samplepin のリストは、APIのレスポンスの中の "results" というキーに格納されている場合と、レスポンス全体がリストになっている場合がある
        # 例えば、{"results": [ {zoo_samplepin1}, {zoo_samplepin2}, ... ]} という形式の場合と、[ {zoo_samplepin1}, {zoo_samplepin2}, ... ] という形式の場合がある
        if isinstance(body, dict) and "results" in body:
            json_data = body["results"]
        # APIのレスポンスがリストの場合は、そのまま利用する
        # 例えば、[ {zoo_samplepin1}, {zoo_samplepin2}, ... ] という形式の場合
        elif isinstance(body, list):
            json_data = body
        # それ以外の形式の場合はエラーとする
        else:
            raise ValueError(f"Unexpected response type for zoo_samplepin: {type(body)}")

        # zoo_samplepin_id に対応するデータをリストから探す
        # 例えば、zoo_samplepin_id が 123 の場合、json_data の中から id が 123 のデータを探す
        # そして、そのデータの isSkip が 1 であればスキップされていると判断する
        # もしも、zoo_samplepin_id に対応するデータが見つからない場合はエラーとする
        for data in json_data:
            if data["id"] == zoo_samplepin_id:
                consumed_time = datetime.now() - start_time
                self.logger.info(f"isSkipped consumed time: {consumed_time}")
                return data["isSkip"] == 1

        raise ValueError(f"zoo_samplepin_id={zoo_samplepin_id} was not found")

    def getCond(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_parameter_samplepin/get_list/"
        response = requests.get(
            target_url,
            headers=auth_headers,
            params={"zoo_samplepin_id": zoo_samplepin_id}
        )

        # APIからのレスポンスが200でない場合はエラーとする
        if response.status_code != 200:
            self.logger.error(f"getCond failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get condition: {response.status_code}")

        # レスポンスの内容を辞書に変換
        cond_dict = response.json()

        # cond_dict が辞書でない場合はエラーとする
        if not isinstance(cond_dict, dict):
            raise ValueError(f"getCond returned non-dict: {type(cond_dict)}")

        # cond_dict が空の場合はエラーとする
        if len(cond_dict) == 0:
            raise ValueError(f"Empty condition returned for zoo_samplepin_id={zoo_samplepin_id}")

        # cond_dict の内容をログに出力
        self.logger.info(f"getCond({zoo_samplepin_id}) keys={sorted(cond_dict.keys())}")
        return cond_dict

    # zoo_samplepin のリストを取得する
    def getSamplePin(self):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/"
        response = requests.get(
            target_url,
            headers=auth_headers,
            params={"zoo_id": self.zoo_id}
        )

        # APIからのレスポンスが200でない場合はエラーとする
        if response.status_code != 200:
            self.logger.error(f"getSamplePin failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get sample pin list: {response.status_code}")

        # レスポンスの内容を辞書に変換
        body = response.json()

        # zoo_samplepin のリストは、APIのレスポンスの中の "results" というキーに格納されている場合と、レスポンス全体がリストになっている場合がある
        # 例えば、{"results": [ {zoo_samplepin1}, {zoo_samplepin2}, ... ]} という形式の場合と、[ {zoo_samplepin1}, {zoo_samplepin2}, ... ] という形式の場合がある   
        if isinstance(body, dict) and "results" in body:
            json_data = body["results"]
        elif isinstance(body, list):
            json_data = body
        else:
            raise ValueError(f"Unexpected response type for zoo_samplepin: {type(body)}")

        # zoo_samplepin のリストをDataFrameに変換して返す
        df = pd.DataFrame(json_data)
        # DataFrameの内容をログに出力
        self.logger.info(f"SamplePin DataFrame shape={df.shape}")
        # DataFrameの列名をログに出力
        self.logger.info(f"SamplePin DataFrame columns={df.columns.tolist()}")

        return df

    # coded by K. Hirata 2024/12/16
    def getCondDataFrame(self):
        self.logger.info("getCondDataFrame starts")
        # zoo_samplepin の取得
        if self.isInit == False:
            self.prep()

        # zoo_samplepin の取得
        df = self.getSamplePin()

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
            # json を dictにして保存
            # 最終的にはリストに追加してDataFrameに変換する
            tmp_dict = self.getCond(zoo_samplepin_id)
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
            if self.token_expiry is None or datetime.now() >= self.token_expiry:
                self.get_access_token()
                self.auth_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
        return self.auth_headers


    def setDone(self, p_index, zoo_samplepin_id, isDone):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/{zoo_samplepin_id}/"

        self.logger.info(f"setDone target_url: {target_url}")
        params = {
            "isDone": isDone,
            "p_index": p_index
        }
        self.logger.info(f"setDone params: {params}")

        # params は data で渡す必要がある（三田さん情報）
        response = requests.put(target_url, headers=auth_headers, data=params)

        self.logger.info(f"setDone status={response.status_code}")
        self.logger.info(f"setDone text={response.text[:1000]}")

        if response.status_code not in (200, 202):
            self.logger.error(f"setDone failed: status={response.status_code}")
            return False

        try:
            json_data = response.json()
            self.logger.info(f"setDone response json: {json_data}")
        except requests.exceptions.JSONDecodeError:
            self.logger.info("setDone response was not JSON, but status was successful")

        return True

    def setSkip(self, p_index, zoo_samplepin_id, isSkip):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/zoo_samplepin/{zoo_samplepin_id}/"

        self.logger.info(f"setSkip target_url: {target_url}")
        data_params = {
            "isSkip": isSkip,
            "p_index": p_index
        }
        self.logger.info(f"setSkip params: {data_params}")

        response = requests.put(target_url, headers=auth_headers, data=data_params)

        self.logger.info(f"setSkip status={response.status_code}")
        self.logger.info(f"setSkip text={response.text[:1000]}")

        if response.status_code not in (200, 202):
            self.logger.error(f"setSkip failed: status={response.status_code}")
            return False

        try:
            json_data = response.json()
            self.logger.info(f"setSkip response json: {json_data}")
        except requests.exceptions.JSONDecodeError:
            self.logger.info("setSkip response was not JSON, but status was successful")

        return True
        
    # post result 
    # param_jsonはJSON形式
    # パラメータのリストは以下のURL先にある
    # https://docs.google.com/spreadsheets/d/1FOFIqBsO4myY7BVIsj6hlMz3fsNlrLBrxmJaJw7bSkQ/edit?gid=2077362619#gid=2077362619
    def postResult(self, sample_pin_id, param_json):
        target_url = f"{self.api_url}zoo_result_samplepin/create_multiple_data/"
        self.logger.info(f"postResult target_url: {target_url}")

        payload = {
            "zoo_samplepin_id": sample_pin_id,
            "data": json.dumps(param_json["data"])
        }
        self.logger.info(f"postResult payload: {payload}")

        auth_headers = self.make_authenticated_request()
        response = requests.post(target_url, headers=auth_headers, json=payload)

        self.logger.info(f"postResult status: {response.status_code}")
        self.logger.info(f"postResult headers: {dict(response.headers)}")
        self.logger.info(f"postResult text: {response.text[:2000]}")

        if response.status_code not in (200, 201):
            self.logger.error(f"postResult failed: status={response.status_code}")
            raise Exception(f"Failed to post result: {response.status_code}")

        try:
            json_data = response.json()
            self.logger.info(f"postResult json: {json_data}")
        except Exception:
            self.logger.info("postResult response was not JSON, but status was successful")

        self.logger.info("postResult posted!!")
        return True

    def getResult(self, sample_pin_id):
        target_url = f"{self.api_url}/zoo_result_samplepin/"
        auth_headers = self.make_authenticated_request()
        response = requests.get(
            target_url,
            headers=auth_headers,
            params={"zoo_samplepin_id": sample_pin_id}
        )

        if response.status_code != 200:
            self.logger.error(f"getResult failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get result: {response.status_code}")

        body = response.json()

        if isinstance(body, dict) and "results" in body:
            json_data = body["results"]
        elif isinstance(body, list):
            json_data = body
        else:
            raise ValueError(f"Unexpected response type for zoo_result_samplepin: {type(body)}")

        result_df = pd.DataFrame(json_data)
        self.logger.info(f"Result DataFrame shape={result_df.shape}")
        return result_df

    def getNextPin(self):
        if self.isInit == False:
            self.prep()

        auth_headers = self.make_authenticated_request()

        query_params = {
            "isDone": 0,
            "isSkip": 0,
            "limit": 1,
            "zoo_id": self.zoo_id
        }

        response = requests.get(self.data_request_url, headers=auth_headers, params=query_params)

        if response.status_code != 200:
            self.logger.error(f"getNextPin failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get next pin: {response.status_code}")

        body = response.json()

        if isinstance(body, dict) and "results" in body:
            results_json = body["results"]
        elif isinstance(body, list):
            results_json = body
        else:
            raise ValueError(f"Unexpected response type for zoo_samplepin: {type(body)}")

        if len(results_json) == 0:
            return None

        dict_results = results_json[0]
        dict_results["zoo_samplepin_id"] = dict_results.pop("id")
        return dict_results

    def convParamname2Paramid(self, parameter_name):
        if not self.isPrepParams:
            self.getParameterList()

        df = self.paramtable_df

        matched = df[df['parameter_name'] == parameter_name]

        if len(matched) == 0:
            self.logger.error(f"Parameter not found: {parameter_name}")
            raise ValueError(f"Parameter not found: {parameter_name}")

        if len(matched) > 1:
            self.logger.warning(f"Multiple parameter IDs found for {parameter_name}, using first")

        param_id = matched.iloc[0]['id']

        self.logger.info(f"param_name={parameter_name} -> param_id={param_id}")
        return param_id

    def getParameterList(self):
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.params_data_url, headers=auth_headers)

        if response.status_code != 200:
            self.logger.error(f"getParameterList failed: {response.status_code}")
            raise Exception("Failed to get parameter list")

        json_data = response.json()
        self.paramtable_df = pd.DataFrame(json_data)
        self.isPrepParams = True

        self.logger.info(f"Parameter list loaded: shape={self.paramtable_df.shape}")

# もしもmainが定義されていない場合以下を実行
if __name__ == '__main__':

    """
    # class をインスタンス化
    esa_loader = ESAloaderAPI(sys.argv[1])
    esa_loader.prep()
    zoo_samplepin_id = 310
    #esa_loader.setDone(999, zoo_samplepin_id, isDone=1)
    #esa_loader.setDone(999, zoo_samplepin_id, isDone=1)
    #esa_loader.postResult(zoo_samplepin_id, {"data":[{"phs_per_deg":"2.3E12"}]})
    esa_loader.postResult(zoo_samplepin_id, {"data":[{"phs_per_deg":"1", "n_mount":"5", "isMount":"1"}]})
    #print(d['isDone'])
    """
    # 2026/04/08のテスト
    exid = sys.argv[1]
    esa = ESAloaderAPI(exid)
    esa.prep()
    print("username=", esa.get_username())
    
    pin = esa.getNextPin()
    print("next pin=", pin)
    
    if pin is not None:
        cond = esa.getCond(pin["zoo_samplepin_id"])
        ok = esa.setDone(pin["p_index"], pin["zoo_samplepin_id"], isDone=pin["isDone"])
        print("setDone result=", ok)
        ok = esa.setSkip(pin["p_index"], pin["zoo_samplepin_id"], pin["isSkip"])
        print("setSkip result=", ok)

        ok = esa.postResult(
                    pin["zoo_samplepin_id"],
            {"data": [
                {"phs_per_deg": "120.0"},
                {"flux": "1.2E12"}
                ]}
        )
        print("postResult result=", ok)

        print("cond keys=", sorted(cond.keys()))
        result_df = esa.getResult(pin["zoo_samplepin_id"])
        print(result_df.columns.tolist())
        print(result_df)

    df = esa.getSamplePin()
    print(df.head())

    """
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