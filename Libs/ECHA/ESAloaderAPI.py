from typing import Any, Optional
import requests
from datetime import datetime, timedelta
# 設定値
import pandas as pd
import json
import logging


class ESAloaderAPI:
    """
    入口は exid のみとし、必要に応じて WebDB から zoo_id を解決して内部利用する。

    <zoo_samplepin>
    zoo_samplepin info は実験条件のヘッダのようなもの
    id: zoo_samplepin_id
    p_index: ピン番号
    isDone: 測定完了フラグ
    isSkip: スキップフラグ
    zoo_id: EXIDに対応するZOOのID
    """

    def __init__(self, exid: str):
        # 既存の api_url 末尾 "/" を維持（原型互換）
        self.api_url = "https://dcha-spx.spring8.or.jp/api1.0.2/"
        self.login_url = "%sdj-rest-auth/login/" % self.api_url
        # self.data_request_url = "%szoo_measure/"%self.api_url
        self.data_request_url = "%szoo_samplepin/" % self.api_url
        self.measure_data_url = "%sparameter_measure/" % self.api_url
        self.params_data_url = "%sparameter/" % self.api_url

        # credential（原型互換のまま）
        # self.username = "admin"
        # self.password = "000nimda"
        self.username = "operator"
        self.password = "1tk2p3640"

        self.token_expiry = None
        self.access_token = None

        # ★追加：exid を保持（入口）
        self.exid = exid

        # Flag in steps
        self.isLogin = False
        self.isExpired = False
        self.isPrepParams = False
        self.isPrepConds = False  # get condition list from DB

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # handler（多重追加を防ぐ：既存挙動を壊さず、二重ログだけ防止）
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            self.logger.addHandler(handler)

            # log file
            log_file = 'esa_loader.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(file_handler)

    # -------------------------
    # Auth
    # -------------------------
    def get_access_token(self):
        # URL
        self.logger.info("Login URL=%s" % self.login_url)
        # post to get access token
        response = requests.post(self.login_url, data={"username": self.username, "password": self.password})
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # token expiry
            last_login = datetime.strptime(token_data['user']['last_login'], '%Y-%m-%dT%H:%M:%S.%f%z')
            # set token expiry by adding 1 hour and removing timezone info
            self.token_expiry = (last_login + timedelta(hours=1)).replace(tzinfo=None)
            # flag
            self.isLogin = True
            self.logger.info("Login successful")
        else:
            self.logger.error("Login failed. status_code=%s" % response.status_code)
            raise Exception("Failed to login")

    def make_authenticated_request(self):
        if self.isLogin is False:
            self.get_access_token()
        else:
            if self.token_expiry is None:
                self.get_access_token()
            elif datetime.now() >= self.token_expiry:
                self.get_access_token()

        self.auth_headers = {"Authorization": f"Bearer {self.access_token}"}
        return self.auth_headers

    # -------------------------
    # ★追加：EXID -> zoo_id 解決
    # -------------------------
    def resolve_zoo_id_from_exid(self) -> int:
        """
        GET api1.0.2/zoo/?exid=XXXX を叩いて zoo_id を得る。
        返り値形式が dict / list のどちらでも壊れにくいように処理する。
        """
        if not self.exid:
            raise ValueError("exid is required to resolve zoo_id")
        # まずheadersなしで GETしてみてだめならば headers付きで再試行
        try:
            # 原型は api_url が末尾 "/" なので、そのまま連結しても "//" になりにくい形
            target_url = f"{self.api_url}zoo/"
            response = requests.get(target_url, params={"exid": self.exid})
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Initial request without auth failed: {e}. Retrying with auth headers.")
            auth_headers = self.make_authenticated_request()
            target_url = f"{self.api_url}zoo/"
            response = requests.get(target_url, headers=auth_headers, params={"exid": self.exid})
            response.raise_for_status()
            data = response.json()

        zoo_id = None
        if isinstance(data, dict):
            zoo_id = data.get("zoo_id") or data.get("id")
        elif isinstance(data, list):
            if len(data) == 0:
                zoo_id = None
            else:
                # 1:1 対応前提なら先頭。複数返る可能性があるならここで弾く設計でもOK。
                zoo_id = data[0].get("zoo_id") or data[0].get("id")

        if zoo_id is None:
            raise LookupError(f"zoo_id not found for exid={self.exid}")

        return int(zoo_id)

    def require_zoo_id(self):
        if self.exid is None:
            raise ValueError("zoo_id is required (or provide exid to resolve zoo_id)")

        self.zoo_id = self.resolve_zoo_id_from_exid()
        self.logger.info(f"[ESAloaderAPI] resolved zoo_id={self.zoo_id} from exid={self.exid}")

    # -------------------------
    # Existing methods (keep)
    # -------------------------
    def isSkipped(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        url = f"{self.api_url}zoo_samplepin/{zoo_samplepin_id}/"
        r = requests.get(url, headers=auth_headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("isSkip") == 1

    def getCond(self, zoo_samplepin_id):
        # access token
        auth_headers = self.make_authenticated_request()
        # get zoo_samplepin information from DB
        target_url = f"{self.api_url}zoo_parameter_samplepin/get_list/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id": zoo_samplepin_id})
        return response.json()

    def getSamplePinInfo(self):
        self.require_zoo_id()
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_samplepin/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_id": self.zoo_id})
        df = pd.DataFrame(response.json())
        self.logger.info("Dataframe: %s" % df)
        return df

    def getCondDataFrame(self):
        self.logger.info("getCondDataFrame starts")
        self.require_zoo_id()

        auth_headers = self.make_authenticated_request()
        # get sample pin list
        df = self.getSamplePinInfo()
        data_list = []
        for i in range(len(df)):
            zoo_samplepin_id = df.iloc[i]["id"]
            self.logger.info("zoo sample pin id: %s" % zoo_samplepin_id)
            # get condition list
            target_url = f"{self.api_url}zoo_parameter_samplepin/get_list/"
            response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id": zoo_samplepin_id})
            data_list.append(response.json())
        self.conds_df = pd.DataFrame(data_list)
        return self.conds_df

    def putCond(self, zoo_parameter_samplepin_id, dict_data):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_parameter_samplepin/{zoo_parameter_samplepin_id}/"
        response = requests.put(target_url, headers=auth_headers, data=dict_data)
        self.logger.info("putCond response status code: %s" % response.status_code)
        return response

    def setDone(self, p_index, zoo_samplepin_id, isDone):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_samplepin/{zoo_samplepin_id}/"
        params= {
            "isDone": isDone,
            "p_index": p_index
        }   
            
        response = requests.put(target_url, headers=auth_headers, data=params)

        if 200 <= response.status_code < 300:
            self.logger.info(f"setDone OK: status={response.status_code}")
            return True
        else:
            self.logger.warning(f"setDone NG: status={response.status_code} body={response.text[:200]}")
            return False

    def setSkip(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_samplepin/{zoo_samplepin_id}/"
        response = requests.patch(target_url, headers=auth_headers, data={"isSkip": 1})
        self.logger.info("setSkip response status code: %s" % response.status_code)
        return response

    def unsetSkip(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_samplepin/{zoo_samplepin_id}/"
        response = requests.patch(target_url, headers=auth_headers, data={"isSkip": 0})
        self.logger.info("unsetSkip response status code: %s" % response.status_code)
        return response

    def postResult(self, dict_result):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_result/"
        response = requests.post(target_url, headers=auth_headers, data=dict_result)
        self.logger.info("postResult response status code: %s" % response.status_code)
        return response

    def getResult(self, zoo_samplepin_id):
        auth_headers = self.make_authenticated_request()
        target_url = f"{self.api_url}zoo_result/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id": zoo_samplepin_id})
        return response.json()

    def getNextPin(self):
        self.require_zoo_id()
        auth_headers = self.make_authenticated_request()
        query_params = {"isDone": 0, "isSkip": 0, "limit": 1, "zoo_id": self.zoo_id}
        response = requests.get(self.data_request_url, headers=auth_headers, params=query_params)
        results_json = response.json()["results"]
        if len(results_json) == 0:
            return None
        dict_results = results_json[0]
        dict_results["zoo_samplepin_id"] = dict_results.pop("id")
        return dict_results

    def convParamname2Paramid(self, dict_params):
        # get params list
        params_list = self.getParameterList()
        # convert dict params
        dict_converted = {}
        for key, value in dict_params.items():
            # get param id from param name
            param_id = None
            for param in params_list:
                if param["parameter_name"] == key:
                    param_id = param["id"]
                    break
            if param_id is None:
                self.logger.warning("Parameter name not found: %s" % key)
                continue
            dict_converted[param_id] = value
        return dict_converted

    def getParameterList(self):
        auth_headers = self.make_authenticated_request()
        response = requests.get(self.params_data_url, headers=auth_headers)
        return response.json()

    def addZOOparams(self, zoo_samplepin_id, dict_params):
        """
        parameter を追加/更新する（原型互換）
        """
        auth_headers = self.make_authenticated_request()

        # get existing parameter list
        target_url = f"{self.api_url}zoo_parameter_samplepin/get_list/"
        response = requests.get(target_url, headers=auth_headers, params={"zoo_samplepin_id": zoo_samplepin_id})
        existing_list = response.json()

        # convert param name -> id
        dict_converted = self.convParamname2Paramid(dict_params)

        # update existing or create new
        for param_id, param_value in dict_converted.items():
            found = False
            for e in existing_list:
                if e.get("parameter_id") == param_id:
                    found = True
                    zoo_parameter_samplepin_id = e["id"]
                    self.putCond(zoo_parameter_samplepin_id, {"value": param_value})
                    break

            if not found:
                # create new
                post_url = f"{self.api_url}zoo_parameter_samplepin/"
                payload = {
                    "zoo_samplepin_id": zoo_samplepin_id,
                    "parameter_id": param_id,
                    "value": param_value
                }
                r = requests.post(post_url, headers=auth_headers, data=payload)
                self.logger.info("addZOOparams create status code: %s" % r.status_code)

        return True
