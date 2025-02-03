# data_collection/api_ds004.py
# https://opendart.fss.or.kr/api/majorstock.json


import requests
import pandas as pd
def fetch_ds004_all(api_key, corp_code, start_date, end_date):
    """
    DS004 대량보유 상황보고 및 임원·주요주주 소유보고 데이터 수집
    """
    # 대량보유 상황보고
    df_majorstock = fetch_ds004_majorstock(api_key, corp_code, start_date, end_date)

    # 임원·주요주주 소유보고
    df_elestock = fetch_ds004_elestock(api_key, corp_code, start_date, end_date)

    return {
        "majorstock": df_majorstock,
        "elestock": df_elestock
    }

def fetch_ds004_elestock(api_key, corp_code, start_date, end_date):
    """
    DS004 임원·주요주주 소유보고 API 호출
    """
    url = "https://opendart.fss.or.kr/api/elestock.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": start_date,
        "end_de": end_date
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "000":
                print(f"[SUCCESS][DS004-EleStock] 데이터 수집 성공: {len(data.get('list', []))}개 항목")
                return pd.DataFrame(data.get("list", []))
            elif data["status"] in ["013", "014"]:
                print(f"[INFO][DS004-EleStock] 데이터 없음: {data['message']}")
            else:
                print(f"[FAIL][DS004-EleStock] API 오류: {data['message']}")
        else:
            print(f"[FAIL][DS004-EleStock] HTTP 요청 실패: {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS004-EleStock] {e}")
    return pd.DataFrame()


def fetch_ds004_majorstock(api_key, corp_code, start_date, end_date):
    """
    DS004 대량보유 상황보고 API 호출
    """
    url = "https://opendart.fss.or.kr/api/majorstock.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bgn_de": start_date,
        "end_de": end_date
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "000":
                print(f"[SUCCESS][DS004-MajorStock] 데이터 수집 성공: {len(data.get('list', []))}개 항목")
                return pd.DataFrame(data.get("list", []))
            elif data["status"] in ["013", "014"]:
                print(f"[INFO][DS004-MajorStock] 데이터 없음: {data['message']}")
            else:
                print(f"[FAIL][DS004-MajorStock] API 오류: {data['message']}")
        else:
            print(f"[FAIL][DS004-MajorStock] HTTP 요청 실패: {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS004-MajorStock] {e}")
    return pd.DataFrame()

