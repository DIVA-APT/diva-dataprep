# data_collection/api_ds005.py

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
                print(f"[ERROR][DS005] API 오류: {json_data['message']}")
        else:
            print(f"[ERROR][DS005] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS005] {e}")
    return pd.DataFrame()  # 실패 시 빈 데이터프레임

def get_major_events(api_key, corp_code, start_date, end_date):
    """
    주요 공시사항 (유상증자, 감자, 합병 등)
    - 예시: 유상증자 결정 API (2020023)
    """
    url = "https://opendart.fss.or.kr/api/piicDecsn.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": start_date,
        "end_de": end_date
    }
    return fetch_data(url, params)

# 필요하다면 감자 결정, 합병 결정 등 API 함수를 추가로 생성
