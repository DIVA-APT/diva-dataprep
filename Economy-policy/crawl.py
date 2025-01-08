from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class Crawl:

    # selenium webdriver 초기화
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

        list = self.get_titles_and_urls_list()
        self.title_list = list['title_list']
        self.url_list = list['url_list']

    # 지표 주제 이름, 하위 페이지 url 리스트 반환
    def get_titles_and_urls_list(self):
        self.driver.get(f'https://ko.tradingeconomics.com/south-korea/1')
        WebDriverWait(self.driver, 100).until(
            expected_conditions.presence_of_element_located((By.TAG_NAME, "body")))

        items = self.driver.find_elements(By.CSS_SELECTOR, '.accordion-item.card-small-spacing')
        result = {'title_list': [], 'url_list': []}

        for item in items:
            result['title_list'].append(item.text)

            urls = []
            for j in item.find_elements(By.TAG_NAME, "a"):
                urls.append(j.get_attribute("href"))

            result['url_list'].append(urls)

        return result

    # 통합
    def all(self, start, end):

        result = ''

        for i in range(start, end):

            result += f'- {self.title_list[i].strip()} 관련 지표\n'

            for url in self.url_list[i]:
                self.driver.get(url)
                WebDriverWait(self.driver, 100).until(
                    expected_conditions.presence_of_element_located((By.TAG_NAME, "html")))

                name = self.driver.find_elements(By.CSS_SELECTOR,
                                                 "#ctl00_ctl06_pageMenu > div > div > div > div > h1 > span.title-indicator")
                if not name: continue

                description = self.driver.find_elements(By.CSS_SELECTOR,
                                                        "#description")
                value = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "#item_definition > div.table-responsive > table > tbody > tr > td:nth-child(2)")
                unit = self.driver.find_elements(By.CSS_SELECTOR,
                                                 "#item_definition > div.table-responsive > table > tbody > tr > td:nth-child(7)")

                result += f' - {name[0].text if name else ""}\n'
                result += f'  - 개요: {description[0].text.rsplit("출처:", 1)[0] if description else "X"}\n'
                result += f'  - 값: {value[0].text if value else ""} ({unit[0].text if unit else ""})\n'

            result += '\n'

        return result
