# params.py
from datetime import datetime
import os
from dotenv import load_dotenv








load_dotenv()  # .env 파일에서 환경 변수 로드

# API Keys
DART_API_KEY = os.getenv("DART_API_KEY")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 기본 설정
CORP_CODE = "00126380"    # 삼성전자 고유번호
CORP_NAME = "삼성전자"

# 보고서 코드 (분기별)
REPORT_CODES = {
    "4Q": "11011",  # 사업보고서 (연간)
    "3Q": "11014",  # 3분기 보고서
    "2Q": "11012",  # 반기보고서
    "1Q": "11013"   # 1분기 보고서
}

# 날짜 설정
CURRENT_YEAR = datetime.now().year
START_YEAR = CURRENT_YEAR - 1  # 현재 연도의 이전 연도부터 탐색 시작
MAX_RETRIES = 3  # 각 API별 최대 반복 횟수 제한

# Pinecone 설정
PINECONE_ENV = "us-east-1"
INDEX_NAME = "fin-index"
EMBEDDING_MODEL = "nlpai-lab/KoE5"
MAX_TOKENS = 512
