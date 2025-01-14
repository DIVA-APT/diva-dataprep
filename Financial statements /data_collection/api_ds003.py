# data_collection/api_ds003.py

import requests
import pandas as pd

def fetch_data(api_url, params):
    """공통 API 호출 함수"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            json_data = resp.json()
            if json_data["status"] == "000":
                return pd.DataFrame(json_data.get("list", []))
            else:
                print(f"[ERROR][DS003] API 오류: {json_data['message']}")
        else:
            print(f"[ERROR][DS003] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS003] {e}")
    return pd.DataFrame()  # 실패 시 빈 데이터프레임

def get_finance_main(api_key, corp_code, year, report_code):
    """
    단일회사 주요계정 (DS003 - 2019016)
    - 재무상태표, 손익계산서 주요 항목
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)

def get_finance_all(api_key, corp_code, year, report_code, fs_div="CFS"):
    """
    단일회사 전체 재무제표 (DS003 - 2019020)
    - IFRS 전체 항목 (CFS=연결, OFS=개별)
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code,
        "fs_div": fs_div
    }
    return fetch_data(url, params)

def get_financial_indicators(api_key, corp_code, year, report_code):
    """
    단일회사 주요 재무지표 (DS003 - 2022001)
    - ROE, ROA, 부채비율, 유동비율 등
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglIndx.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)
