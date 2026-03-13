# Tech Stack — pyq001
# Elliott Wave TA Quant System

---

## 확정 스택

| 컴포넌트 | 선택 | 이유 |
|---------|------|------|
| Language | Python 3.11+ | 퀀트 생태계 최강, ccxt/pandas-ta 풀 지원 |
| Exchange API | ccxt 4.3+ | 통합 API, Binance Futures 지원, async 지원 |
| OHLCV 저장 | Apache Parquet (pyarrow) | 컬럼형 압축, pandas 직접 읽기, 빠른 I/O |
| Knowledge Base | SQLite (sqlalchemy 2.0) | 로컬 경량, 복잡한 쿼리 불필요, 이식성 |
| TA 보조 | pandas-ta | 순수 Python, ta-lib 설치 불필요 |
| LLM (파싱) | Claude API (claude-sonnet-4-6) | 한국어+영어 텍스트→JSON 파싱 최적 |
| 이미지 분석 | Qwen2.5-VL (로컬, optional) | EGP CNO 모델 라우팅 일치, 무료 |
| Config | python-dotenv + pyyaml | API 키 환경변수 분리 |
| Async | asyncio + aiohttp + websockets | WebSocket 실시간 스트림 |
| Test | pytest + pytest-asyncio | 표준 Python 테스트 |
| Backtest | 자체 경량 엔진 | 의존성 최소화, Wave 시스템 맞춤 |

---

## 보류 (Phase별 검토)

| 컴포넌트 | 상태 | 검토 시점 |
|---------|------|---------|
| vectorbt | 보류 | Phase 3 — 자체 백테스트 엔진 대비 성능 비교 후 결정 |
| Redis/BullMQ | 보류 | Phase 5 멀티마켓 확장 시 필요 여부 판단 |
| Telegram Bot | 보류 | Phase 5 유지 레이어 구성 시 |
| TimescaleDB | 보류 | 대용량 실시간 데이터 시 parquet 대체 검토 |

---

## 모델 라우팅 (EGP CNO 기준)

```
텍스트→JSON 파싱    : Claude API (claude-sonnet-4-6)
차트 이미지 분석    : Qwen2.5-VL 로컬 (optional)
OHLCV 수집/처리     : 로컬 ccxt + pandas (LLM 없음)
파동 탐지/계산      : 로컬 Python 연산 (LLM 없음)
백테스트            : 로컬 Python 연산 (LLM 없음)
```

API 비용 최소화: Learning Layer 입력 시에만 Claude API 호출.
런타임 트레이딩 루프에서는 LLM 호출 없음.

---

## Python 환경

```bash
# 권장 Python
python --version  # 3.11+

# 설치
pip install -r requirements.txt
```

---

## 실행 환경

```
Mac Mini M4 (메인 서버)
  - Phase 1~3: 개발 + 백테스트
  - Phase 4~5: 24/7 자동 실행 (tmux)

MacBook Air (원격)
  - ssh macmini.local (Tailscale)
  - tmux attach
```
