# PHASE_1.md — pyq001
# EGP v4.0 | Phase 1: 설계 + 데이터 레이어

---

## Phase 1 목표

프로젝트 기반 구조 완성 및 데이터 레이어 구현.
이후 모든 Phase의 토대가 되는 안정적인 OHLCV 수집/저장 파이프라인 확보.

---

## 임계 지표

```
완료 조건 1: BTC/USDT 1h 500개 캔들 수집 성공 (ccxt)
완료 조건 2: parquet 저장 + 로드 사이클 완료 (데이터 무결성 확인)
완료 조건 3: pytest test_data.py 전체 통과
```

---

## 산출물 정의 (CPO 검증 기준)

Phase 1 완료 시 반드시 존재해야 하는 것:

- [x] CLAUDE.md EGP 헤더 삽입 완료
- [x] /egp/council/roles.yaml 작성 완료
- [x] /egp/triggers/thresholds.yaml 작성 완료
- [x] /egp/phases/PHASE_1~5.md 초안
- [x] /config/config.yaml 작성 완료
- [x] /docs/architecture.md 작성 완료
- [x] /docs/tech_stack.md 작성 완료
- [x] /src/data/fetcher.py — ccxt OHLCV 구현 완료
- [x] /src/data/storage.py — parquet 저장/로드 구현 완료
- [x] /src/data/preprocessor.py — 전처리 구현 완료
- [x] /tests/test_data.py 통과 (10/10 PASSED)

---

## 기술 스택 결정

```
Language    : Python 3.11+
Exchange    : ccxt >= 4.3.0 (Binance Futures)
Data Store  : parquet (pyarrow) for OHLCV
             SQLite (sqlalchemy) for knowledge base (Phase 2)
TA          : pandas-ta (보조 지표)
LLM         : anthropic SDK (claude-sonnet-4-6)
Async       : asyncio + aiohttp
Config      : python-dotenv + pyyaml
Test        : pytest + pytest-asyncio
Infra       : Mac Mini M4 로컬
```

---

## 리스크 사전 정의 (CRO)

```
리스크 1: ccxt API 레이트 리밋 초과
          대응: 요청 간 delay 추가, 배치 크기 제한 (1000개/요청)

리스크 2: 타임존 불일치 (UTC vs KST)
          대응: 전체 시스템 UTC 통일, 출력 시에만 KST 변환

리스크 3: 데이터 갭 (거래소 다운타임)
          대응: 결측 구간 로그 기록, 보간 불가 시 해당 구간 제외

리스크 4: parquet 파일 손상
          대응: 저장 후 즉시 checksum 검증
```

---

## Phase 완료 시 보고서 트리거

Phase 1 완료 조건 달성 시:

1. 즉시 실행 정지
2. `/egp/reports/phase_1_report.md` 생성 (6섹션 양식)
3. Chairman에게 보고 텍스트 출력
4. Chairman 승인 대기

---

## 다음 Phase 예고

Phase 2: TA Learning Layer (Text→JSON 파싱) + Wave Decision Tree Engine 구현
         (Wave 탐지 설계는 Chairman과 별도 심층 협의 후 확정)

---

*EGP v4.0 | pyq001 | Phase 1*
