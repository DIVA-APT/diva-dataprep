# data_collection/api_ds001.py

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
                print(f"[ERROR][DS001] API 오류: {json_data['message']}")
        else:
            print(f"[ERROR][DS001] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS001] {e}")
    return pd.DataFrame()  # 실패 시 빈 데이터프레임

def get_company_info(api_key, corp_code):
    """
    기업개황(회사 기본정보) 조회 (DS001 - 2019002)
    - 회사명, 업종, 대표자명, 설립일 등
    """
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code
    }
    df = fetch_data(url, params)
    return df

