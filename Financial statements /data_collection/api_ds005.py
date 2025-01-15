# data_collection/api_ds005.py

import requests
import pandas as pd

def fetch_ds005(api_url, params):
    """공통 API 호출 함수 for DS005"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "000":
                return pd.DataFrame(data.get("list", []))
            else:
                print(f"[DS005 ERROR] {data['message']}")
        else:
            print(f"[DS005 ERROR] HTTP {resp.status_code}")
    except Exception as e:
        print(f"[DS005 EXCEPTION] {e}")
    return pd.DataFrame()

def get_major_disclosures(api_key, corp_code, start_date, end_date):
    """
    유상증자결정 등(DS005 - 예: 2020023)
    """
    url = "https://opendart.fss.or.kr/api/piicDecsn.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": start_date,
        "end_de": end_date
    }
    df = fetch_ds005(url, params)
    return df
