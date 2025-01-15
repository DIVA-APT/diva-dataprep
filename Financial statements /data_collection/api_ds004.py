# data_collection/api_ds004.py

import requests
import pandas as pd

def fetch_ds004(api_url, params):
    """공통 API 호출 함수 for DS004"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "000":
                return pd.DataFrame(data.get("list", []))
            else:
                print(f"[DS004 ERROR] {data['message']}")
        else:
            print(f"[DS004 ERROR] HTTP {resp.status_code}")
    except Exception as e:
        print(f"[DS004 EXCEPTION] {e}")
    return pd.DataFrame()

def get_major_stock_info(api_key, corp_code):
    """
    대량보유 상황보고 or 임원·주요주주 소유보고 (DS004)
    실제 구현 시 URL, 파라미터, API ID에 맞춰 작성
    """
    # 예시만 제시
    url = "https://opendart.fss.or.kr/api/stocks.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        # ...
    }
    df = fetch_ds004(url, params)
    return df
