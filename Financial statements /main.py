# main.py

import time
from datetime import datetime

from generate_report.report_generator import generate_one_page_report
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경 변수 로드
API_KEY = os.getenv("DART_API_KEY")
##########################
# 설정
##########################
CORP_CODE = "00126380"     # 삼성전자 예시
COLLECT_TIME = "06:00"     # 정해진 시간
# 테스트에서는 즉시 실행

# 보고서코드 예(최신 보고서가 3분기라 가정)
TARGET_YEAR = datetime.now().year
REPORT_CODE = "11014"  # 3분기
START_DATE = (datetime.now().replace(year=datetime.now().year - 1)).strftime("%Y%m%d")  # 1년전
END_DATE = datetime.now().strftime("%Y%m%d")

##########################
# 스케줄링 로직 (주석처리)
##########################
def wait_until_collect_time():
    while True:
        now_time = datetime.now().strftime("%H:%M")
        if now_time == COLLECT_TIME:
            print("[INFO] 스케줄 시간 도달. 데이터 수집 및 리포트 생성 시작.")
            generate_one_page_report(API_KEY, CORP_CODE, TARGET_YEAR, REPORT_CODE, START_DATE, END_DATE)
            break
        time.sleep(30)

##########################
# 메인 실행
##########################
if __name__ == "__main__":
    print("[INFO] 테스트 버전: 즉시 실행으로 데이터 수집 및 리포트 생성")
    # 실제 운영 시:
    # wait_until_collect_time()
    # 여기서는 테스트 용도로 즉시 실행
    generate_one_page_report(API_KEY, CORP_CODE, TARGET_YEAR, REPORT_CODE, START_DATE, END_DATE)
