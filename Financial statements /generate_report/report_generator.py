# generate_report/report_generator.py

import pandas as pd

# DS001
from data_collection.api_ds001 import get_company_info

# DS002
from data_collection.api_ds002 import get_major_shareholder_info, get_audit_opinion

# DS003
from data_collection.api_ds003 import get_entire_financials, get_financial_indicators

# DS005
from data_collection.api_ds005 import get_major_disclosures


def check_df_status(df: pd.DataFrame, label: str) -> bool:
    """
    데이터프레임이 비어 있지 않으면 True를 리턴하고,
    비어 있으면 False를 리턴하며 메시지 출력.
    """
    if df.empty:
        print(f"[FAIL] {label}: 데이터를 가져오지 못했습니다.")
        return False
    else:
        print(f"[OK] {label}: 데이터 {len(df)}개 항목을 가져왔습니다.")
        return True


def generate_report_for_period(api_key, corp_code, bsns_year, reprt_code):
    """
    특정 (년도 + 보고서코드)에 대해
    재무제표 + 재무지표 + 최대주주 + 감사의견 등 가져와서 상태 출력
    """
    print(f"\n=== [재무제표 수집] {bsns_year}년, 보고서코드({reprt_code}) ===")

    df_fin = get_entire_financials(api_key, corp_code, bsns_year, reprt_code, fs_div="CFS")
    check_df_status(df_fin, f"전체 재무제표(CFS) {bsns_year}년-{reprt_code}")

    df_indicators = get_financial_indicators(api_key, corp_code, bsns_year, reprt_code)
    check_df_status(df_indicators, f"주요 재무지표 {bsns_year}년-{reprt_code}")

    df_shareholder = get_major_shareholder_info(api_key, corp_code, bsns_year, reprt_code)
    check_df_status(df_shareholder, f"최대주주 현황 {bsns_year}년-{reprt_code}")

    df_audit = get_audit_opinion(api_key, corp_code, bsns_year, reprt_code)
    check_df_status(df_audit, f"감사의견 {bsns_year}년-{reprt_code}")


def generate_overall_report(api_key, corp_code):
    """
    1) 회사 개황
    2) 최근 3개 재무제표 (최신 분기부터 역순으로)
    3) 주요 공시사항
    """
    print("\n[1] 회사 개황 정보")
    df_company = get_company_info(api_key, corp_code)
    check_df_status(df_company, "기업개황")

    print("\n[2] 최근 3개의 재무제표 수집 시도")
    # 여기서 최근 4분기(11011)를 최우선으로 하고,
    # 없으면 3분기(11014), 2분기(11012), 1분기(11013) 순서
    # 2025년 1월 가정 -> 2024년 4분기가 존재하면 첫 번째
    # 존재하지 않으면 3분기, 그 다음 없으면 2분기, 1분기 -> 그래도 부족하면 2023년 4분기...

    quarter_priority = [("4Q", "11011"), ("3Q", "11014"), ("2Q", "11012"), ("1Q", "11013")]
    # 우선 2024년부터 검사, 없으면 2023년으로 넘어감 etc.

    found_count = 0
    current_year = 2024
    while found_count < 3 and current_year >= 2022:  # 임의로 2022년까지만 시도
        for (q_label, rc) in quarter_priority:
            if found_count >= 3:
                break
            # 재무제표 가져오기 시도
            # 단순히 get_entire_financials를 호출해서 df가 비어있는지 판단
            df_fin = get_entire_financials(api_key, corp_code, current_year, rc, "CFS")
            if df_fin.empty:
                print(f"[INFO] {current_year}년 {q_label}({rc}) 데이터 없음, 다음 분기 확인.")
            else:
                print(f"[SUCCESS] {current_year}년 {q_label}({rc}) 데이터 확인 → 리포트 생성.")
                # 리포트 생성 (주요 재무제표 + 재무지표 + 최대주주 + 감사의견)
                generate_report_for_period(api_key, corp_code, current_year, rc)
                found_count += 1
            if found_count >= 3:
                break
        current_year -= 1

    print(f"[INFO] 최근 {found_count}개의 재무제표 수집 완료.")

    print("\n[3] 주요 공시사항(DS005) 최근 1년")
    # 가정: 20240101~20250101 범위로 조회
    # 실제 날짜 계산은 필요한 대로 조정
    start_date = "20240101"
    end_date = "20250101"
    from data_collection.api_ds005 import get_major_disclosures
    df_disclosures = get_major_disclosures(api_key, corp_code, start_date, end_date)
    check_df_status(df_disclosures, f"주요사항보고서 ({start_date}~{end_date})")
    print("[INFO] 보고서 생성 프로세스 완료.\n")
