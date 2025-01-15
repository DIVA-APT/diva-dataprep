# data_collection/api_ds003.py

import requests
import pandas as pd

def fetch_ds003(api_url, params):
    """공통 API 호출 함수 for DS003"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data["status"] == "000":
                return pd.DataFrame(data.get("list", []))
            else:
                print(f"[DS003 ERROR] {data['message']}")
        else:
            print(f"[DS003 ERROR] HTTP {resp.status_code}")
    except Exception as e:
        print(f"[DS003 EXCEPTION] {e}")
    return pd.DataFrame()

def get_entire_financials(api_key, corp_code, bsns_year, reprt_code, fs_div="CFS"):
    """
    단일회사 전체 재무제표 (DS003 - 2019020)
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code,
        "fs_div": fs_div
    }
    df = fetch_ds003(url, params)
    return df

def get_financial_indicators(api_key, corp_code, bsns_year, reprt_code):
    """
    단일회사 주요 재무지표 (DS003 - 2022001)
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglIndx.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code
    }
    df = fetch_ds003(url, params)
    return df
