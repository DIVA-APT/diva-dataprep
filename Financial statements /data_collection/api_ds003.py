# api_ds003.py

import requests
import pandas as pd


def fetch_ds003(api_url, params):
    """
    공통 API 호출 함수 for DS003
    """
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "")
            if status == "000":
                print(f"[SUCCESS][DS003] 데이터 수집 성공: {len(data.get('list', []))}개 항목")
                return pd.DataFrame(data.get("list", []))
            elif status in ["013", "014"]:
                print(f"[INFO][DS003] 데이터 없음: {data['message']}")
            else:
                print(f"[FAIL][DS003] API 오류: {data['message']}")
        else:
            print(f"[FAIL][DS003] HTTP 요청 실패: {response.status_code}")
    except Exception as e:
        print(f"[EXCEPTION][DS003] {e}")
    return pd.DataFrame()


def get_entire_financials(api_key, corp_code, bsns_year, reprt_code, fs_div="CFS"):
    """
    단일회사 주요계정 (DS003 - 2019016)
    - 재무제표 항목 (자산, 부채, 자본 등)을 가져옴.
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglAcnt.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code,
        "fs_div": fs_div  # CFS(연결재무제표) 또는 OFS(개별재무제표)
    }
    return fetch_ds003(url, params)


def get_financial_indicators(api_key, corp_code, bsns_year, reprt_code):
    """
    단일회사 주요 재무지표 (DS003 - 2022001)
    - ROE, 부채비율 등 주요 지표를 가져옴.
    """
    url = "https://opendart.fss.or.kr/api/fnlttSinglIndx.json"
    params = {
        "crtfc_key": api_key,
        "corp_code": corp_code,
        "bsns_year": str(bsns_year),
        "reprt_code": reprt_code,
        # 필수 파라미터 추가 (예: 수익성 지표)
        "idx_cl_code": "M210000"  # 수익성 지표 코드 (예: ROE, 영업이익률 등)
    }
    return fetch_ds003(url, params)

