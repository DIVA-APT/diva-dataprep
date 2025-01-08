from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 웹 페이지 URL
URL = 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020301'

def KRX_Data():
    driver = webdriver.Chrome()
    output_file = "output_data.txt"  # 출력 파일명

    def extract_institution_and_foreign_data(driver, output_file):
        # 페이지 로드
        driver.get(URL)

        # 테이블 데이터가 로드될 때까지 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "CI-GRID-ODD"))
            )
        except Exception as e:
            print("테이블 로딩 오류:", e)
            return

        # 페이지 소스를 BeautifulSoup으로 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 데이터 추출
        rows = soup.find_all('tr', class_=['CI-GRID-ODD', 'CI-GRID-EVEN'])
        volume_columns = ["매도", "매수", "순매수"]
        value_columns = ["매도대금", "매수대금", "순매수대금"]

        with open(output_file, 'w', encoding='utf-8') as f:
            for row in rows:
                cells = row.find_all('td')
                if cells:
                    category = cells[0].text.strip()
                    if category in ['기관합계', '개인', '외국인']:
                        values = [cell.text.strip().replace(',', '') for cell in cells[1:]]  # 콤마 제거
                        volume_data = ", ".join([f"{col}: {val}" for col, val in zip(volume_columns, values[:3])])
                        value_data = ", ".join([f"{col}: {val}" for col, val in zip(value_columns, values[3:])])
                        data_line = f"{category}\n거래량: {volume_data}\n거래대금: {value_data}\n"
                        f.write(data_line)
                        print(data_line)  # 콘솔에도 출력

    try:
        extract_institution_and_foreign_data(driver, output_file)
    finally:
        driver.quit()



# if __name__ == "__main__":
#     main()
