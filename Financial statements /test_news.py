import json
import uuid
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import numpy as np
import torch
from params import PINECONE_API_KEY
# pinecone, sentence_transformers 등이 설치되어 있어야 함
import pinecone
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from utils.news_utils import (
    fetch_article_title_and_body_multi,
    generate_naver_news_url,
    extract_news_urls,
    clean_text,
    preprocess_text,
    normalize_data,
    # chunk_text_koe5,
    # embed_chunks_koe5,
    # upsert_article_to_pinecone,
    # query_similar_chunks,
    # verify_duplicates,
    # check_article_duplicate
)
from utils.general_utils import (
    chunk_text_koe5,
    embed_chunks_koe5,
    upsert_article_to_pinecone,
    query_similar_chunks,
    verify_duplicates,
    check_article_duplicate
)
def process_article_with_embedding(doc_id, title, content, url, keyword, koe5_model):
    """
    기사 본문(clean_text 후) -> chunk -> koe5 임베딩 -> article_data에 삽입
    """
    # 우선 clean_text로 본문 정제
    cleaned_body = clean_text(content)

    # chunking (512 tokens)
    #from utils.news_utils import chunk_text_koe5, embed_chunks_koe5  # 이미 작성된 함수라 가정
    chunks = chunk_text_koe5(cleaned_body, max_tokens=512)

    # KoE5 임베딩
    embeddings_tensor = embed_chunks_koe5(chunks, koe5_model)  # (num_chunks, 768)
    embeddings = embeddings_tensor.cpu().numpy().tolist()

    # 최종 article_data
    article_data = {
        "doc_id": doc_id,
        "title": title.strip(),
        "content": cleaned_body,
        "source_url": url,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "stock": keyword,
        "category": "news",
        # embeddings 배열을 기사 데이터에 직접 포함
        "embeddings": embeddings,
        "chunks": chunks
    }
    return article_data

if __name__ == "__main__":
    ###################################
    # 1) 파라미터 및 초기 설정
    ###################################
    keyword = "현대모비스"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    start_date_str = start_date.strftime("%Y.%m.%d")
    end_date_str = end_date.strftime("%Y.%m.%d")
    from pinecone import Pinecone

    # # Pinecone 설정
    #us - east - 1

    PINECONE_API_KEY = PINECONE_API_KEY
    PINECONE_ENV = "us-east-1"       # ex: "us-west1-gcp"
    INDEX_NAME = "news-index"            # ex: "news-index"

    # KoE5 모델 로드
    koe5_model = SentenceTransformer("nlpai-lab/KoE5")

    # # Pinecone 초기화
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Index 생성 (존재하지 않을 경우)
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=1024,  # KoE5 임베딩 차원
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        )

    pinecone_index = pc.Index(INDEX_NAME)

    #pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    # if INDEX_NAME not in pinecone.list_indexes():
    #     pinecone.create_index(INDEX_NAME, dimension=1024)  # KoE5 벡터 차원
    # pinecone_index = pinecone.Index(INDEX_NAME)

    ###################################
    # 2) 뉴스 크롤링
    ###################################
    search_url = generate_naver_news_url(keyword, start_date_str, end_date_str)
    print(f"\n[INFO] 검색 URL: {search_url}")

    news_urls = extract_news_urls(search_url, max_pages=5)
    print(f"\n=== 총 수집된 뉴스 링크 수: {len(news_urls)} ===")

    articles = []
    for url in news_urls:
        title, body = fetch_article_title_and_body_multi(url)

        # 50자 이하인 것은 무의미하다고 가정
        if len(body) <= 50:
            print("수집된 뉴스 기사-->  50자 이하로 제외함")
            continue

        # 노이즈 제거
        cleaned_body = clean_text(body)

        doc_id = str(uuid.uuid4())
        article_data = process_article_with_embedding(doc_id, title, cleaned_body, url, keyword, koe5_model)
        # article_data = {
        #     "doc_id": doc_id,
        #     "title": title,
        #     "content": cleaned_body,
        #     "stock": keyword,
        #     "category": "news",
        #     "date": datetime.now().strftime("%Y-%m-%d"),
        #     "source_url": url
        # }
        #article_data = normalize_data(article_data)
        articles.append(article_data)

    print(f"\n수집 완료된 기사 수(중복 제거 후): {len(articles)}")

    ###################################
    # 3) JSON 로컬 저장 (디버깅용)
    ###################################
    filename = f"naver_news_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"\n[INFO] 임시로 {len(articles)}개 기사를 {filename}에 저장했습니다.")

    ###################################
    # 4) 중복 검사 → 비중복이면 업서트
    ###################################

    upsert_count = 0
    skip_count = 0

    for article in articles:
        new_article_text = article["content"]

        # (a) 중복 검사
        # check_article_duplicate 함수가
        # 1) chunk+embed
        # 2) Pinecone 쿼리
        # 3) threshold 이상이면 True
        is_dup = check_article_duplicate(
            article_text=new_article_text,
            koe5_model=koe5_model,
            pinecone_index=pinecone_index,
            date_limit_days=3,  # 최근 3일 내 문서만 비교
            top_k=5,
            threshold=0.8       # 임계값
        )

        if is_dup:
            print(f"[중복] 문서 {article['doc_id']} - {article['title']} => Upsert 생략")
            skip_count += 1
            continue

        # (b) 비중복이면 업서트
        upsert_article_to_pinecone(
            doc_id=article["doc_id"],
            title=article["title"],
            article_text=new_article_text,
            source_url=article["source_url"],
            date_str=article["date"],
            pinecone_index=pinecone_index,
            koe5_model=koe5_model,
            max_tokens=512
        )
        print(f"[업서트 완료] 문서 {article['doc_id']} - {article['title']}")
        upsert_count += 1

    print(f"\n=== 업서트 완료 결과 ===")
    print(f" - 중복으로 인해 스킵된 기사 수: {skip_count}")
    print(f" - 업서트된 비중복 기사 수: {upsert_count}")


    print("[INFO] 전체 로직 종료.")
