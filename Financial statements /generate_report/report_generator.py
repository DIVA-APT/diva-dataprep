# generate_report/report_generator.py

from datetime import datetime
from data_collection.api_ds001 import get_company_info
from data_collection.api_ds002 import get_major_shareholder_info, get_audit_opinion
from data_collection.api_ds003 import get_entire_financials, get_financial_indicators
from data_collection.api_ds004 import fetch_ds004_majorstock, fetch_ds004_elestock
from data_collection.api_ds005 import get_major_disclosures
from data_preprocessor import process_financial_data, upsert_vectors
from params import REPORT_CODES, CORP_CODE


def get_latest_quarter_data(api_key, corp_code, api_func, max_quarters_back=4):
    """
    현재 분기부터 시작하여 데이터가 있는 가장 최신 분기를 탐색.
    """
    current_year = datetime.now().year
    current_quarter = (datetime.now().month - 1) // 3 + 1

    for i in range(max_quarters_back):
        year = current_year
        quarter = current_quarter - i

        if quarter < 1:
            year -= 1
            quarter += 4

        report_code = REPORT_CODES[f"{quarter}Q"]

        data = api_func(api_key, corp_code, year, report_code)
        if data is not None and not data.empty:
            return data, year, quarter  # 데이터와 함께 연도 및 분기를 반환

    return None, None, None  # 데이터가 없으면 None 반환


def generate_one_page_report(api_key: str, corp_code: str, start_year: int, max_retries: int):
    end_year = datetime.now().year

    # 1. 기업 기본 정보 수집 (분기 정보 없음)
    company_info = get_company_info(api_key, corp_code)
    if company_info is not None:
        vectors = process_financial_data(company_info, "company_info", end_year, quarter=0)  # quarter=0
        upsert_vectors(vectors)

    # 2. 주요 공시사항 (분기 정보 없음)
    disclosures = get_major_disclosures(api_key, corp_code, f"{start_year}0101", f"{end_year}1231")
    if disclosures is not None:
        vectors = process_financial_data(disclosures, "disclosures", end_year, quarter=0)  # quarter=0
        upsert_vectors(vectors)

    # 3. 재무제표 데이터 (최신 분기부터 탐색)
    financials, fin_year, fin_quarter = get_latest_quarter_data(api_key, corp_code, get_entire_financials)
    if financials is not None:
        vectors = process_financial_data(financials, "financials", fin_year, fin_quarter)  # quarter=fin_quarter
        upsert_vectors(vectors)

    # 4. 재무 지표 데이터 (최신 분기부터 탐색)
    indicators, ind_year, ind_quarter = get_latest_quarter_data(api_key, corp_code, get_financial_indicators)
    if indicators is not None:
        vectors = process_financial_data(indicators, "indicators", ind_year, ind_quarter)  # quarter=ind_quarter
        upsert_vectors(vectors)

    # 5. 주요 주주 정보 (최신 분기부터 탐색)
    shareholders, sh_year, sh_quarter = get_latest_quarter_data(api_key, corp_code, get_major_shareholder_info)
    if shareholders is not None:
        vectors = process_financial_data(shareholders, "shareholders", sh_year, sh_quarter)  # quarter=sh_quarter
        upsert_vectors(vectors)

    # 6. 감사 의견 (최신 분기부터 탐색)
    audit_opinion, audit_year, audit_quarter = get_latest_quarter_data(api_key, corp_code, get_audit_opinion)
    if audit_opinion is not None:
        vectors = process_financial_data(audit_opinion, "audit_opinion", audit_year, audit_quarter)  # quarter=audit_quarter
        upsert_vectors(vectors)

    # 7. 대량보유 상황 (분기 정보 없음)
    majorstock = fetch_ds004_majorstock(api_key, corp_code, f"{start_year}0101", f"{end_year}1231")
    if majorstock is not None:
        vectors = process_financial_data(majorstock, "majorstock", end_year, quarter=0)  # quarter=0
        upsert_vectors(vectors)

    # 8. 임원·주요주주 소유보고 (분기 정보 없음)
    elestock = fetch_ds004_elestock(api_key, corp_code, f"{start_year}0101", f"{end_year}1231")
    if elestock is not None:
        vectors = process_financial_data(elestock, "elestock", end_year, quarter=0)  # quarter=0
        upsert_vectors(vectors)

    return {
        "company_info": company_info,
        "latest_financials": {
            "year": fin_year,
            "quarter": fin_quarter,
            "data": financials
        },
        "latest_indicators": {
            "year": ind_year,
            "quarter": ind_quarter,
            "data": indicators
        }
    }
