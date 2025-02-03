import json
from datetime import datetime
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import pandas as pd
from params import *

# KoE5 모델 초기화
koe5_model = SentenceTransformer(EMBEDDING_MODEL)

# Pinecone 초기화
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    )
index = pc.Index(INDEX_NAME)


def chunk_text_koe5(text: str, max_tokens: int = MAX_TOKENS) -> list:
    words = text.split()
    return [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]


def process_financial_data(data: pd.DataFrame, report_type: str, year: int, quarter: int) -> list:
    """
    재무 데이터를 처리하여 Pinecone 업서트에 필요한 벡터와 메타데이터를 생성합니다.
    """
    vectors = []

    # DataFrame의 각 행을 처리
    records = data.to_dict('records')  # 각 행을 딕셔너리로 변환

    for i, record in enumerate(records):
        # 전체 데이터를 JSON 문자열로 변환
        raw_data = json.dumps(record, ensure_ascii=False)  # JSON 문자열로 변환

        # 메타데이터 생성
        metadata = {
            "corp_code": CORP_CODE,
            "report_type": report_type,
            "year": year,
            "quarter": quarter,  # 최종 가져온 분기 정보 추가
            "chunk_index": i,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "raw_data": raw_data  # JSON 문자열로 저장
        }

        # ID 생성
        vector_id = f"{CORP_CODE}_{report_type}_{year}_Q{quarter}_{i}"

        # 임베딩 생성 (raw_data를 JSON 문자열로 변환)
        embedding = koe5_model.encode(raw_data).tolist()

        # 벡터 추가
        vectors.append((vector_id, embedding, metadata))

    return vectors


def upsert_vectors(vectors: list):
    """
    Pinecone 업서트 전에 JSON 파일로 저장하고 업서트 수행
    """
    if not vectors:
        print("[WARNING] No vectors to upsert.")
        return

    # JSON 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"vectors_to_upsert_{timestamp}.json"
    save_vectors_to_json(vectors, filename)
    print(f"[INFO] Vector metadata saved to {filename}")

    try:
        index.upsert(vectors=vectors)
        print(f"[SUCCESS] {len(vectors)} vectors upserted to Pinecone")
    except Exception as e:
        print(f"[ERROR] Upsert failed: {str(e)}")
        print(f"[INFO] You can check the vector metadata in {filename}")


def save_vectors_to_json(vectors: list, filename: str):
    """
    벡터 데이터를 JSON 파일로 저장 (임베딩 제외)
    """
    json_data = []
    for vec in vectors:
        json_data.append({
            "id": vec[0],
            "metadata": vec[2]  # 메타데이터만 저장
        })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

