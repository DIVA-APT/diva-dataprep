# data_collection/api_ds005.py
import requests
import pandas as pd

def fetch_ds005(api_url, params):
    """공통 API 호출 함수 for DS005"""
    try:
        resp = requests.get(api_url, params=params)
        if resp.status_code == 200:
            json_data = resp.json()
            status = json_data.get("status", "")
            if status == "000":
                print(f"[SUCCESS][DS005] 데이터 수집 성공: {len(json_data.get('list', []))}개 항목")
                return pd.DataFrame(json_data.get("list", []))
            elif status in ["013", "014"]:
                print(f"[INFO][DS005] 데이터 없음: {json_data['message']}")
            else:
                print(f"[FAIL][DS005] API 오류: {json_data['message']}")
        else:
            print(f"[FAIL][DS005] HTTP 요청 실패: {resp.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS005] {e}")
    return pd.DataFrame()

def get_major_disclosures(api_key, corp_code, start_date, end_date):
    """
    주요 공시사항 (유상증자 등) - DS005 예시
    """
    url = "https://opendart.fss.or.kr/api/piicDecsn.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        # 필수 파라미터 추가
        "bgn_de": start_date,
        "end_de": end_date
    }
    return fetch_ds005(url, params)
