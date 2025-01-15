# data_collection/api_ds002.py

import requests
import pandas as pd

def fetch_ds002(api_url, params):
    """공통 API 호출 함수 for DS002"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "000":
                return pd.DataFrame(data.get("list", []))
            else:
                print(f"[DS002 ERROR] {data['message']}")
        else:
            print(f"[DS002 ERROR] HTTP {resp.status_code}")
    except Exception as e:
        print(f"[DS002 EXCEPTION] {e}")
    return pd.DataFrame()

def get_major_shareholder_info(api_key, corp_code, bsns_year, reprt_code):
    """
    최대주주 현황 (DS002-2019007)
    """
    url = "https://opendart.fss.or.kr/api/hyslrSttus.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code
    }
    df = fetch_ds002(url, params)
    return df

def get_audit_opinion(api_key, corp_code, bsns_year, reprt_code):
    """
    감사의견 (DS002 - 2020009)
    """
    url = "https://opendart.fss.or.kr/api/accnutAdtorNmNdAdtOpinion.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code
    }
    df = fetch_ds002(url, params)
    return df
