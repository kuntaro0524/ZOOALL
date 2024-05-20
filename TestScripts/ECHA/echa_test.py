import requests
from datetime import datetime, timedelta

# 設定値
API_URL = "https://dcha-spx.spring8.or.jp/api1.0.2/"
LOGIN_URL = "%sdj-rest-auth/login/"%API_URL
DATA_REQUEST_URL = "%szoo_measure/"%API_URL
MEASURE_DATA_URL = "%sparameter_measure/"%API_URL
USERNAME = "admin"
PASSWORD = "000nimda"
token_expiry = None
access_token = None
import pandas as pd

def get_access_token():
    global access_token, token_expiry
    print("EEEEEEEEEEEEEEEEEE")
    print(LOGIN_URL, USERNAME, PASSWORD)
    response = requests.post(LOGIN_URL, data={"username": USERNAME, "password": PASSWORD})
    if response.status_code == 200:
        token_data = response.json()
        print(token_data)
        access_token = token_data['access_token']
        # トークンが作成された時刻は 'last_login' に格納されている
        # この時間に１時間を足した時間がトークンの有効期限
        # format '2024-04-25T07:21:34.153331+09:00'
        last_login = datetime.strptime(token_data['user']['last_login'], "%Y-%m-%dT%H:%M:%S.%f%z")
        expiry = last_login + timedelta(hours=1)
        print("Expired" , expiry)

    else:
        raise Exception("Failed to login")

def make_authenticated_request():
    global access_token, token_expiry
    # トークンの有効期限が切れているか確認
    if token_expiry is None or datetime.now() >= token_expiry:
        get_access_token()  # トークンが切れていたら新しく取得
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(DATA_REQUEST_URL, headers=headers, params={"zoo_id":2})
    # response を pandas DataFrame に変換
    # print(response.json())
    df = pd.DataFrame(response.json())

    # df の１行ずつのデータ取得
    # この辞書をリストに追加していく
    data_list = []
    for i in range(len(df)):
        # 'measure_id' を取得
        meas_id=df.iloc[i]['measure_id']
        target_url = f"{API_URL}/parameter_measure/"
        response = requests.get(target_url, headers=headers, params={"measure_id":meas_id})
        print(response.json())
        each_df = pd.DataFrame(response.json())
        print(each_df.columns)
        dicts = {}
        for j in range(len(each_df)):
        # この each_df に含まれている１行のデータの 'parameter_name' と 'value' で dictionaryを作成
            dicts[each_df.iloc[j]['parameter_name']] = each_df.iloc[j]['value']

        # dicts を Series に変換
        each_pin_df = pd.Series(dicts)
        # print(each_pin_df)
        data_list.append(each_pin_df)

    # data_list からpandas DataFrameを作成
    conds_df = pd.DataFrame(data_list)
    # print(conds_df)

    return conds_df

# データを取得する関数を使用
start_time = datetime.now()
conds_df = make_authenticated_request()
print("#####################")
for each_cond in conds_df.iterrows():
    print(each_cond)
print("#####################")

end_time = datetime.now()
# 消費時間を計算 (sec)
consumed_time = end_time - start_time
print("Consumed Time: ", consumed_time)

