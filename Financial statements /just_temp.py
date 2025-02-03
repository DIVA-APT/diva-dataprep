from datetime import datetime, timedelta
from utils.news_utils import try_newspaper, try_trafilatura, try_selenium, try_basic_bs
import requests
from bs4 import BeautifulSoup
import json
import re
import uuid


# ===========================
# 함수 정의
# ===========================

def fetch_article_title_and_body_multi(url):


# 기존 코드와 동일

def generate_naver_news_url(keyword, start_date, end_date):


# 기존 코드와 동일

def extract_news_urls(search_url):


# 기존 코드와 동일

def clean_text(text):
    """
    기사 본문에서 노이즈를 제거하는 함수
    """
    # 광고 문구 제거
    text = re.sub(r"\[.*?재판매 및 DB 금지.*?\]", "", text)
    # 기자 정보 제거
    text = re.sub(r"\(.*?기자\)|\n.*?기자", "", text)
    # 불필요한 공백 제거
    text = re.sub(r"\s+", " ", text).strip()
    return text


def chunk_text(text, max_tokens=512):
    """
    긴 텍스트를 max_tokens 단위로 나누는 함수
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunks.append(" ".join(words[i:i + max_tokens]))
    return chunks


# ===========================
# 실행 코드 (__main__)
# ===========================

if __name__ == "__main__":
    # 기존 코드와 동일 (키워드 설정, URL 생성, 뉴스 URL 추출 등)

    articles = []
    success_count = 0
    fail_count = 0

    for url in news_urls:
        title, body = fetch_article_title_and_body_multi(url)
        if len(body) > 50:
            # 노이즈 제거
            cleaned_body = clean_text(body)
            # 청크 분할
            chunks = chunk_text(cleaned_body)

            doc_id = str(uuid.uuid4())  # 고유 ID 생성
            article_data = {
                "doc_id": doc_id,
                "title": title,
                "content": cleaned_body,
                "embedding": [],  # 임베딩 벡터는 별도로 생성해야 함
                "stock": "삼성전자",  # 예시 값, 실제로는 동적으로 설정해야 함
                "category": "뉴스",  # 예시 값, 실제로는 동적으로 설정해야 함
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source_url": url,
                "chunks": chunks
            }
            articles.append(article_data)
            success_count += 1
        else:
            fail_count += 1

    # 결과 출력 (기존 코드와 동일)

    # JSON으로 저장
    filename = f"naver_news_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

    print(f"\n[INFO] 총 {len(articles)}개의 기사를 {filename}에 저장했습니다.")
