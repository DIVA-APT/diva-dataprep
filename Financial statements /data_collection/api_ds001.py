# data_collection/api_ds001.py

import requests
import pandas as pd

def fetch_ds001(api_url, params):
    """공통 API 호출 함수 for DS001"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "000":
                return pd.DataFrame(data.get("list", []))
            else:
                print(f"[DS001 ERROR] {data['message']}")
        else:
            print(f"[DS001 ERROR] HTTP {resp.status_code}")
    except Exception as e:
        print(f"[DS001 EXCEPTION] {e}")
    return pd.DataFrame()

def get_company_info(api_key, corp_code):
    """
    기업개황 API (DS001-2019002)
    """
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code
    }
    df = fetch_ds001(url, params)
    return df
