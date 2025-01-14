# generate_report/report_generator.py

import pandas as pd
from datetime import datetime

# DS001
from data_collection.api_ds001 import get_company_info

# DS002
from data_collection.api_ds002 import (
    get_dividend_info,
    get_major_shareholder_info,
    get_audit_opinion,
    get_manager_info
)

# DS003
from data_collection.api_ds003 import (
    get_finance_main,
    get_finance_all,
    get_financial_indicators
)

# DS005
from data_collection.api_ds005 import get_major_events

##################
# 리포트 셀프체크
##################
def check_dataframe(df: pd.DataFrame, item_name: str):
    """데이터프레임이 비어있지 않은지 확인 후 결과 출력"""
    if df.empty:
        print(f"[FAIL] '{item_name}' 데이터 없음 또는 수집 실패.")
    else:
        print(f"[OK] '{item_name}' 데이터 수집 성공. 레코드 수: {len(df)}")
        # 필요시 df.head() 등 출력 가능

##################
# 리포트 생성
##################
def generate_one_page_report(api_key, corp_code,
                             target_year, report_code,
                             start_date, end_date):
    """
    최종 리포트 생성:
    1) 회사 개황
    2) 재무상태(재무제표)
    3) 손익(매출, 영업이익, 당기순이익, EPS, R&D ...)
    4) 주요 재무지표(ROE, ROA, 부채비율, 유동비율, OCF 등)
    5) 주식 관련 정보(최대주주, 배당, 자기주식 등)
    6) 주요 공시사항(유무상증자, 합병, 채권발행, 소송 등)
    7) 감사 의견 및 경영진 정보(감사의견, 임원현황, 보수현황 등)
    """

    print("\n========== [1. 회사 개황] ==========")
    df_company = get_company_info(api_key, corp_code)
    check_dataframe(df_company, "회사 개황")

    print("\n========== [2. 재무상태 & 3. 손익 요약] ==========")
    # 단일회사 전체 재무제표(연결기준) 사용
    df_fin_all = get_finance_all(api_key, corp_code, target_year, report_code, fs_div="CFS")
    check_dataframe(df_fin_all, "단일회사 전체 재무제표")

    print("\n========== [4. 주요 재무지표] ==========")
    df_fin_index = get_financial_indicators(api_key, corp_code, target_year, report_code)
    check_dataframe(df_fin_index, "단일회사 주요 재무지표")

    print("\n========== [5. 주식 관련 정보 (배당, 최대주주 등)] ==========")
    df_dividend = get_dividend_info(api_key, corp_code, target_year, report_code)
    check_dataframe(df_dividend, "배당 정보")

    df_major_holder = get_major_shareholder_info(api_key, corp_code, target_year, report_code)
    check_dataframe(df_major_holder, "최대주주 현황")

    # 필요 시 자기주식, 소액주주, 공모자금 등 DS002에서 더 추가

    print("\n========== [6. 주요 공시사항 (DS005)] ==========")
    df_events = get_major_events(api_key, corp_code, start_date, end_date)
    check_dataframe(df_events, "주요 공시사항")

    print("\n========== [7. 감사 의견 및 경영진 정보] ==========")
    df_audit = get_audit_opinion(api_key, corp_code, target_year, report_code)
    check_dataframe(df_audit, "감사의견")

    df_manager = get_manager_info(api_key, corp_code, target_year, report_code)
    check_dataframe(df_manager, "임원 현황")

    print("\n[INFO] 리포트 생성 완료. 필요시 각 DF 가공하여 최종 1페이지로 요약 표기 가능.")
