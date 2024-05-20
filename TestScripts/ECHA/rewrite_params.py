from typing import Any
import requests
from datetime import datetime, timedelta
# 設定値
import pandas as pd

class ESAloader:
    def __init__(self, api_url):
        self.api_url = api_url
        self.api_url = "https://dcha-spx.spring8.or.jp/api1.0.2/"
        self.login_url = "%sdj-rest-auth/login/"%self.api_url
        self.data_request_url = "%szoo_measure/"%self.api_url
        self.measure_data_url = "%sparameter_measure/"%self.api_url
        self.params_data_url = "%sparameter/"%self.api_url
        self.username = "admin"
        self.password = "000nimda"
        self.token_expiry = None
        self.access_token = None

        # Flag in steps
        self.isLogin = False
        self.isExpired = False

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
            self.isLogin = True
        else:
            print("Exception!!!!!!!!!!!")
            raise Exception("Failed to login")

    def getCondDataFrame(self):
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.data_request_url, headers=auth_headers, params={"zoo_id":2})
        # response を pandas DataFrame に変換
        # print(response.json())
        df = pd.DataFrame(response.json())

        # df の１行ずつのデータ取得
        # この辞書をリストに追加していく
        data_list = []
        for i in range(len(df)):
            # 'measure_id' を取得
            meas_id=df.iloc[i]['measure_id']
            target_url = f"{self.api_url}/parameter_measure/"
            response = requests.get(target_url, headers=auth_headers, params={"measure_id":meas_id})
            print(response.json())
            each_df = pd.DataFrame(response.json())
            print(each_df.columns)
            dicts = {}
            for j in range(len(each_df)):
            # この each_df に含まれている１行のデータの 'parameter_name' と 'value' で dictionaryを作成
                dicts[each_df.iloc[j]['parameter_name']] = each_df.iloc[j]['value']
                # measure_idを追加する
                dicts['measure_id'] = meas_id

            # dicts を Series に変換
            each_pin_df = pd.Series(dicts)
            # print(each_pin_df)
            data_list.append(each_pin_df)

        # data_list からpandas DataFrameを作成
        conds_df = pd.DataFrame(data_list)
        # print(conds_df)

        return conds_df

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
        # convert 'parameter_name' to 'parameter_id'

        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}/parameter_measure/"
        response = requests.post(target_url, headers=auth_headers, data={"measure_id":measure_id, "parameter_name":parameter_name, "value":value})
        print(response.json())

    def getParameterList(self):
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.params_data_url, headers=auth_headers)
        print(response.json())
        json_data = response.json()
        df_params = pd.DataFrame(json_data)
        df_params.to_csv('params.csv')

# class をインスタンス化
esa_loader = ESAloader("https://dcha-spx.spring8.or.jp/api1.0.2/")
# ログイン
esa_loader.make_authenticated_request()

# データを取得する関数を使用
# start_time = datetime.now()
# esa_loader.getParameterList()

# 条件を新たに追加したらどうなるか？
# putCond(19854, "isDone", True)

# conds_df = getCondDataFrame()
# print("#####################")
# for each_cond in conds_df.iterrows():
#     print(each_cond)
# print("#####################")

# end_time = datetime.now()
# # 消費時間を計算 (sec)
# consumed_time = end_time - start_time
# print("Consumed Time: ", consumed_time)

# csv_file_path = 'received.csv'
# conds_df.to_csv(csv_file_path)
