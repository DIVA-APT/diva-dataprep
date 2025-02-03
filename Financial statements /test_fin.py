# test_fin.py
import time
from generate_report.report_generator import generate_one_page_report
from params import DART_API_KEY, CORP_CODE, START_YEAR, MAX_RETRIES

COLLECT_TIME = "06:00"  # 스케줄링 시간

def wait_until_collect_time():
    """
    매일 정해진 COLLECT_TIME까지 대기 후 실행.
    """
    while True:
        now_time = time.strftime("%H:%M")
        if now_time == COLLECT_TIME:
            print(f"[INFO] 스케줄 시각 {COLLECT_TIME} 도달. 데이터 수집 및 리포트 생성 시작.")
            generate_one_page_report(DART_API_KEY, CORP_CODE, START_YEAR, MAX_RETRIES)
            break
        time.sleep(30)

if __name__ == "__main__":
    print("[INFO] 테스트 버전 - 즉시 실행 (스케줄링 주석 처리)")
    # 실제 운영 시: wait_until_collect_time()
    generate_one_page_report(DART_API_KEY, CORP_CODE, START_YEAR, MAX_RETRIES)
