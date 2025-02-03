# data_collection/api_ds002.py
import requests
import pandas as pd

def fetch_ds002(api_url, params):
    """공통 API 호출 함수 for DS002"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            json_data = resp.json()
            status = json_data.get("status", "")
            if status == "000":
                print(f"[SUCCESS][DS002] 데이터 수집 성공: {len(json_data.get('list', []))}개 항목")
                return pd.DataFrame(json_data.get("list", []))
            elif status in ["013", "014"]:
                print(f"[INFO][DS002] 데이터 없음: {json_data['message']}")
            else:
                print(f"[FAIL][DS002] API 오류: {json_data['message']}")
        else:
            print(f"[FAIL][DS002] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS002] {e}")
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
    return fetch_ds002(url, params)

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
    return fetch_ds002(url, params)
