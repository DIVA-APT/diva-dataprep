# main.py

import time
from datetime import datetime

from generate_report.report_generator import generate_overall_report
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일에서 환경 변수 로드
API_KEY = os.getenv("DART_API_KEY")
##########################



CORP_CODE = "00126380"  # 예시: 삼성전자
COLLECT_TIME = "06:00"


def wait_until_collect_time():
    while True:
        now = datetime.now().strftime("%H:%M")
        if now == COLLECT_TIME:
            print(f"\n[INFO] 스케줄 시각 {COLLECT_TIME} 도달. 데이터 수집 및 리포트 생성 시작.")
            generate_overall_report(API_KEY, CORP_CODE)
            break
        time.sleep(30)


if __name__ == "__main__":
    print("[INFO] 테스트 버전 - 즉시 실행 (스케줄링 주석 처리)")
    # 실제 운영 시:  wait_until_collect_time()

    generate_overall_report(API_KEY, CORP_CODE)

