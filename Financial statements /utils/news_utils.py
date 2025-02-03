from bs4 import BeautifulSoup
from newspaper import Article
import trafilatura
import re
# (동적 자바스크립트 페이지용) Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import requests
import numpy as np

################################
# 기존 import
################################
# transformers, sentence_transformers 등은 사용 환경에 맞게 import
# 예: from sentence_transformers import SentenceTransformer
# 예: import pinecone

################################
# 사용 함수 정리 (fetch_article_title_and_body_multi 등)
'''
fetch_article_title_and_body_multi: 크롤링 시도 4단계 함수
generate_naver_news_url: 네이버 뉴스 검색 URL 생성 함수
extract_news_urls: 여러 페이지에서 뉴스 URL을 추출하는 함수
clean_text: 기사 본문에서 노이즈를 제거하는 함수
chunk_text: 긴 텍스트를 max_tokens 단위로 나누는 함수

'''
# 1. 노이즈 제거
# def remove_noise(text):
#     """광고, 저작권 문구, 기자 정보 등 불필요한 정보 제거"""
#     # 이미 clean_text 함수에서 구현되어 있습니다.
#     return clean_text(text)

# 2. 데이터 정규화
def normalize_data(article_data):
    """날짜 형식 통일, 제목과 본문 구분 등"""
    article_data['date'] = datetime.strptime(article_data['date'], "%Y-%m-%d").strftime("%Y-%m-%d")
    article_data['title'] = article_data['title'].strip()
    article_data['content'] = article_data['content'].strip()
    return article_data

# 3. 중복 데이터 처리
# def remove_duplicates(articles):
#     """중복된 기사 식별 및 제거"""
#     seen = set()
#     unique_articles = []
#     for article in articles:
#         if article['title'] not in seen:
#             seen.add(article['title'])
#             unique_articles.append(article)
#     return unique_articles

# 5. 텍스트 전처리
def preprocess_text(text):
    """토큰화, 불용어 제거, 문장 분리 등"""
    # 간단한 토큰화 예시
    tokens = re.findall(r'\w+', text.lower())
    # 불용어 제거 (예시)
    stopwords = set(['은', '는', '이', '가', '을', '를', '의', '에', '에서'])
    tokens = [token for token in tokens if token not in stopwords]
    return tokens
################################

def fetch_article_title_and_body_multi(url):
    """
    [멀티 라이브러리 + fallback]
    1) newspaper3k
    2) trafilatura
    3) selenium
    4) basic_bs
    순서로 시도 -> 먼저 성공 시 반환

    + 만약 모두 실패라면, "가져올 수 없습니다" 메시지
    """
    print(f"\n[fetch_article_title_and_body_multi] URL: {url}")

    # 1) newspaper3k
    title, body = try_newspaper(url)
    if len(body) > 50:
        return title, body

    # 2) trafilatura
    title, body = try_trafilatura(url)
    if len(body) > 50:
        return title, body

    # 3) selenium
    title, body = try_selenium(url, driver_path="/usr/bin/chromedriver")
    if len(body) > 50:
        return title, body

    # 4) basic_bs
    title, body = try_basic_bs(url)
    if len(body) > 50:
        return title, body

    # 모두 실패
    print(f" >>> {url}은(는) 가져올 수 없습니다.")
    return "", ""


def generate_naver_news_url(keyword, start_date, end_date):
    """
    네이버 뉴스 검색 URL 생성 함수
    """
    base_url = "https://search.naver.com/search.naver"
    query = f"?where=news&query={keyword}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={start_date}&de={end_date}"
    return base_url + query


def extract_news_urls(search_url, max_pages=5):
    """
    여러 페이지에서 뉴스 URL을 추출하는 함수
    """
    news_links = []
    for page in range(1, max_pages + 1):
        url = f"{search_url}&start={(page-1)*10+1}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.select(".news_tit"):
            link = a_tag['href']
            news_links.append(link)
    return news_links


def clean_text(text):
    """
    불필요한 문자와 문구를 제거해 기사 본문을 정제합니다.
    - '기자' 정보, '무단전재', '재판매 금지' 등
    - 대괄호와 그 안의 내용을 제거
    - 불필요한 공백, 특수문자 처리
    """
    # 1) 기자 문구 & 저작권 문구 제거
    text = re.sub(r"\(.*?기자\)|\n.*?기자|저작권자|무단전재|재배포|AI학습.*?금지", "", text, flags=re.IGNORECASE)  # [2][10]

    # 2) 대괄호 안 내용 제거 (예: [사진=...], [이데일리...])
    text = re.sub(r"\[.*?\]", "", text)

    # 3) 따옴표 안 특수문자 정리 (예시)
    #    필요하다면, `<`, `>` 같은 HTML 태그 제거
    text = re.sub(r"<.*?>", "", text)

    # 4) 남은 여러 공백을 단일 공백으로
    text = re.sub(r"\s+", " ", text).strip()

    return text


def chunk_text(text, max_tokens=512):
    """
    chunk_text긴 텍스트를 max_tokens 단위로 나누는 함수
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))
    return chunks

################################
# 아래 함수들은 그대로 유지
################################

def try_newspaper(url):
    """
    newspaper3k 라이브러리를 사용해 기사 제목과 본문을 추출.
    """
    print(" - [try_newspaper3k] 시도 중...")
    try:
        from newspaper import Article
        article = Article(url, language='ko')
        article.download()
        article.parse()
        title = article.title.strip() if article.title else ""
        text = article.text.strip() if article.text else ""
        if len(text) > 50:
            print("   => newspaper3k 추출 성공!")
            return title, text
        else:
            print("   >> newspaper3k: 본문이 너무 짧음.")
    except Exception as e:
        print(f"   >> newspaper3k 오류: {e}")
    return "", ""


def try_trafilatura(url):
    """
    trafilatura로 기사 제목, 본문 추출
    """
    print(" - [try_trafilatura] 시도 중...")
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text and len(text) > 50:
                soup = BeautifulSoup(downloaded, 'html.parser')
                t_tag = soup.find('title')
                title = t_tag.get_text(strip=True) if t_tag else ""
                print("   => trafilatura 추출 성공!")
                return title, text
            else:
                print("   >> trafilatura: 추출된 본문이 너무 짧음.")
        else:
            print("   >> trafilatura: URL fetch 실패.")
    except Exception as e:
        print(f"   >> trafilatura 오류: {e}")
    return "", ""


def try_selenium(url, driver_path="/usr/bin/chromedriver"):
    """
    Selenium으로 자바스크립트 렌더링 후, <title> + <p> 태그 단순 합침
    """
    print(" - [try_selenium] 시도 중...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))

        title = driver.title.strip()
        paragraphs = driver.find_elements(By.TAG_NAME, 'p')
        texts = [p.text.strip() for p in paragraphs if p.text.strip()]
        content = "\n".join(texts)

        driver.quit()

        if len(content) > 50:
            print("   => selenium 추출 성공!")
            return title, content
        else:
            print("   >> selenium: 본문이 너무 짧음.")
    except Exception as e:
        print(f"   >> selenium 오류: {e}")
    return "", ""


def try_basic_bs(url):
    """
    requests + BeautifulSoup로 <title>과 모든 <p> 합치는 최소한의 fallback
    """
    print(" - [try_basic_bs] 시도 중...")
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else ""

        paragraphs = soup.find_all('p')
        body = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        if len(body) > 50:
            print("   => basic_bs 추출 성공!")
            return title, body
        else:
            print("   >> basic_bs: 본문이 너무 짧음.")
    except Exception as e:
        print(f"   >> basic_bs 오류: {e}")

    return "", ""
