## 제무제표 데이터 수집 구조

```sh
├─Financial statements
│  │  README.md
│  │  main.py
│  ├─data_collection
│  │      api_ds001.py
│  │      api_ds002.py
│  │      api_ds003.py
│  │      api_ds005.py
│  └─generate_report
│          report_generator.py
```


## data_collection/
- **api_ds001.py**: DS001(공시정보) API (기업개황, 공시검색 등)  
- **api_ds002.py**: DS002(정기보고서 주요정보) API (배당, 최대주주, 감사의견, 임원현황 등)  
- **api_ds003.py**: DS003(정기보고서 재무정보) API (단일회사 주요계정, 전체 재무제표 등)  
- **api_ds004.py**: DS004(지분공시) API (대량보유 상황보고, 임원·주요주주 소유보고)  
- **api_ds005.py**: DS005(주요사항보고서) API (유상증자, 합병, 감자, 소송 등)

## generate_report/
- **report_generator.py**:  
  - DART API 모듈을 import하여 최종 리포트 생성  
  - 항목별(회사개황, 재무상태, 손익, 재무지표, 주식정보, 공시사항, 감사의견 등) 데이터 수집 및 출력

## main.py
- 환경설정(API_KEY, CORP_CODE 등)  
- 스케줄링(예: 06:00) 제어 (테스트 시 즉시 실행)  
- 최종적으로 `report_generator.py` 호출하여 한 페이지 리포트 작성
