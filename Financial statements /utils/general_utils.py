import numpy as np
import torch
from typing import List, Dict
import datetime
import re
# chunk_text_koe5, embed_chunks_koe5, upsert_article_to_pinecone, query_similar_chunks, verify_duplicates

# pinecone, sentence_transformers 등이 이미 설치/임포트되어 있어야 함
# from sentence_transformers import SentenceTransformer
# import pinecone



############################################
# 1. TEXT CHUNKING (512 tokens)
############################################

def chunk_text_koe5(text: str, max_tokens: int = 512) -> List[str]:
    """
    문단 대신 'max_tokens' 단위로 텍스트를 잘라 리스트로 반환.
    KoE5의 max_tokens=512 제약을 고려.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens):
        chunk_str = " ".join(words[i:i + max_tokens])
        chunks.append(chunk_str)
    return chunks


############################################
# 2. EMBEDDING (KoE5)
############################################

def embed_chunks_koe5(chunks: List[str], koe5_model) -> torch.Tensor:
    """
    KoE5 모델로 각 청크를 임베딩한 뒤, (num_chunks, vector_dim) 형태의 Tensor 반환.
    """
    embeddings = koe5_model.encode(chunks, convert_to_tensor=True)
    return embeddings


############################################
# 3. UPSERT TO PINECONE
############################################

def upsert_article_to_pinecone(doc_id: str,
                               title: str,
                               article_text: str,
                               date_str: str,
                               source_url: str,  # [추가] 기사 원본 URL
                               pinecone_index,
                               koe5_model,
                               max_tokens: int = 512
                               ) -> None:
    """
    기사 본문을 chunk → KoE5 임베딩 → Pinecone에 업서트.

    구조 예시:
      id = f"{doc_id}_chunk_{i}"
      metadata = {
        "doc_id": doc_id,
        "title": title,
        "date": date_str,
        "chunk_index": i,
        "source_url": source_url,  # [추가]
        "chunk": "청크된 텍스트"    # [추가]
      }
      values = (koe5 임베딩 벡터)
    """
    # 1) chunking
    chunks = chunk_text_koe5(article_text, max_tokens)

    # 2) embedding
    embeddings = embed_chunks_koe5(chunks, koe5_model)  # (num_chunks, dim)
    embeddings_np = embeddings.cpu().numpy()

    # 3) upsert
    vectors_to_upsert = []
    for i, vec in enumerate(embeddings_np):
        chunk_id = f"{doc_id}_chunk_{i}"
        metadata = {
            "doc_id": doc_id,
            "title": title,
            "date": date_str,
            "chunk_index": i,
            "source_url": source_url,  # [추가] 기사 URL
            "chunk": chunks[i]  # [추가] 청크 본문
        }
        vectors_to_upsert.append((chunk_id, vec.tolist(), metadata))

    # Pinecone upsert
    pinecone_index.upsert(vectors=vectors_to_upsert)


############################################
# 4. ANN SEARCH + TIME WINDOW FILTER
############################################

def query_similar_chunks(article_text: str,
                         koe5_model,
                         pinecone_index,
                         date_limit_days: int = 3,
                         top_k: int = 5,
                         threshold: float = 0.8
                         ) -> List[Dict]:
    """
    새 기사가 들어올 때: chunk & embed → Pinecone ANN 검색.
    'date_limit_days' = 최근 며칠 이내 문서만 검색 (metadata 필터).
    top_k개 후보만 가져옴 → threshold로 중복 판별.

    Returns: 후보 chunk들의 id, score, metadata 리스트.
    """
    # 1) chunk & embed
    chunks = chunk_text_koe5(article_text, 512)
    embeddings = embed_chunks_koe5(chunks, koe5_model).cpu().numpy()

    # 2) time window filter
    # - 오늘 날짜 기준 date_limit_days일 이내인 문서만 검색
    # Pinecone의 metadata 필드(date)가 "YYYY-MM-DD" 형태라고 가정
    # date 필터: n일 이내인 조건 설정 (Pinecone metadata filter 예시).
    # ex) filter_conditions = { "date": { "$gte": "2023-10-01" } }
    # 다만 pinecone는 숫자/boolean이 아니면 범위쿼리가 제한적이므로,
    # 연/월/일을 별도필드로 저장하거나, RFC3339형식 사용 등 별도 처리 필요.

    # 여기서는 단순 예시로 filter 없이 진행 (실제론 날짜 파싱 후 filter 만듦)
    filter_conditions = None

    # 3) ANN 검색 (상위 top_k)
    results = []
    for vec in embeddings:
        query_res = pinecone_index.query(
            vector=vec.tolist(),
            top_k=top_k,
            include_metadata=True,
            filter=filter_conditions
        )
        results.append(query_res)

    # 4) score(유사도) 기반 중복판별
    #   - Pinecone 기본 distance가 'cosine'이면, score = 1 - distance or similarity
    #   - 설정에 따라 score 해석이 달라질 수 있음(주의!)
    #   - threshold 이상인 것만 "중복"으로 본다고 가정

    # 최종 후보 리스트 구조화
    final_candidates = []
    for res in results:
        for match in res.matches:
            candidate = {
                "id": match.id,
                "score": match.score,  # pinecone에서는 similarity or distance
                "metadata": match.metadata,
                "is_duplicate": (match.score >= threshold)
            }
            final_candidates.append(candidate)

    return final_candidates


############################################
# 5. BATCH 유사도 정밀 비교 (Optional)
############################################

def verify_duplicates(candidates: List[Dict], full_article_embedding: np.ndarray = None):
    """
    ANN 검색으로 얻은 후보(candidates)에 대해
    추가 정밀 비교가 필요하다면 TF-IDF나 코사인 재계산 등 수행.
    여기서는 예시로 단순히 candidate["is_duplicate"]만 리턴.
    """
    # 실제로는 여기서 full_article_embedding과 candidate chunk 임베딩 간
    # 코사인 유사도를 다시 측정해 threshold 재판단 가능
    return [c for c in candidates if c["is_duplicate"]]


############################################
# 6. 최종 중복 판정: yes/no
############################################

def check_article_duplicate(article_text: str,
                            koe5_model,
                            pinecone_index,
                            date_limit_days: int = 3,
                            top_k: int = 5,
                            threshold: float = 0.8) -> bool:
    """
    전체 로직 종합:
    1) chunk+embed
    2) Pinecone ANN 검색 (3일 제한, top_k)
    3) threshold 이상이면 중복 판정
    4) 하나라도 중복이면 True
    """
    candidates = query_similar_chunks(article_text, koe5_model, pinecone_index,
                                      date_limit_days, top_k, threshold)
    # 정밀 검사 (선택)
    duplicates = verify_duplicates(candidates)
    return (len(duplicates) > 0)
