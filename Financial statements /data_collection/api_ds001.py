# data_collection/api_ds001.py
import requests
import pandas as pd

def fetch_ds001(api_url, params):
    """공통 API 호출 함수 for DS001"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            json_data = resp.json()
            status = json_data.get("status", "")
            if status == "000":
                print(f"[SUCCESS][DS001] 데이터 수집 성공: {len(json_data.get('list', []))}개 항목")
                return pd.DataFrame([json_data])  # JSON 전체를 DataFrame으로 변환
            elif status in ["013", "014"]:
                print(f"[INFO][DS001] 데이터 없음: {json_data['message']}")
            else:
                print(f"[FAIL][DS001] API 오류: {json_data['message']}")
        else:
            print(f"[FAIL][DS001] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS001] {e}")
    return pd.DataFrame()

def get_company_info(api_key, corp_code):
    """
    기업개황 (DS001-2019002)
    """
    url = "https://opendart.fss.or.kr/api/company.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code
    }
    return fetch_ds001(url, params)
