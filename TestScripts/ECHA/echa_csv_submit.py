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

def submit_csv_file(csv_file):
    global access_token, token_expiry
    # トークンの有効期限が切れているか確認
    if token_expiry is None or datetime.now() >= token_expiry:
        get_access_token()  # トークンが切れていたら新しく取得
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # submit URL
    submit_url = f"{API_URL}zoo/"
    print("CSV submitted to ", submit_url)
    print(csv_file)
    response = requests.post(submit_url, headers=headers, files={'file': open(csv_file, 'rb')})

    print(response.json())

# データを取得する関数を使用
start_time = datetime.now()
import sys,os
csv_file = sys.argv[1]
abs_path = os.path.abspath(csv_file)
conds_df = submit_csv_file(abs_path)