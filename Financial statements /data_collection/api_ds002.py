# data_collection/api_ds002.py

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
                print(f"[ERROR][DS002] API 오류: {json_data['message']}")
        else:
            print(f"[ERROR][DS002] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS002] {e}")
    return pd.DataFrame()  # 실패 시 빈 데이터프레임

def get_dividend_info(api_key, corp_code, year, report_code):
    """
    배당에 관한 사항 (DS002 - 2019005)
    - 배당금, 배당성향 등
    """
    url = "https://opendart.fss.or.kr/api/alotMatter.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)

def get_major_shareholder_info(api_key, corp_code, year, report_code):
    """
    최대주주 현황 (DS002 - 2019007)
    - 최대주주, 소액주주 등
    """
    url = "https://opendart.fss.or.kr/api/hyslrSttus.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)

def get_audit_opinion(api_key, corp_code, year, report_code):
    """
    회계감사인의 명칭 및 감사의견 (DS002 - 2020009)
    """
    url = "https://opendart.fss.or.kr/api/accnutAdtorNmNdAdtOpinion.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)

def get_manager_info(api_key, corp_code, year, report_code):
    """
    임원 현황 (DS002 - 2019010) 및
    보수현황 등 다양한 DS002 API를 추가 연결 가능
    """
    url = "https://opendart.fss.or.kr/api/exctvSttus.json"  # 임원현황 API(2019010)
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": report_code
    }
    return fetch_data(url, params)
