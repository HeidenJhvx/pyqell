# CLAUDE.md — EGP v4.0
# Project: pyq001 — Elliott Wave TA Quant System
# Chairman: qy3R | qy3R OS

---

## ⚠️ EGP GOVERNANCE RULES

이 프로젝트는 EGP v4.0 (간소화) 적용을 받는다.
전체 규칙: `/egp/EGP_PROTOCOL.md` 참조

### 핵심 규칙
1. **Phase 완료 시 즉시 실행 정지** — 다음 Phase로 넘어가지 말 것
2. **표준 보고서 생성** — `/egp/reports/phase_N_report.md` 작성
3. **Chairman 승인 없이 Phase 전환 금지**
4. **Directive 수신 즉시 반영**
5. **모든 구성 변경은 파일로 저장 후 git commit**

---

## 프로젝트 정보

```
Project      : pyq001 — Elliott Wave TA Quant System
Mode         : Bootstrap
Current Phase: 1
EGP Version  : v4.0 (간소화 — Phase Gate + Threshold만 유지)
Telegram Bot : 미설정 (Phase 5 이후 유지 레이어 추가)
Autonomy     : Level 0 (Bootstrap)
```

---

## 현재 Phase 정보

```
Phase 1 목표    : 아키텍처 확정 + 데이터 레이어 구현
임계 지표       : ccxt OHLCV 수집 + parquet 저장 + 로드 성공
산출물          : 프로젝트 구조, EGP 문서, src/data/ 구현 완료
완료 조건       : BTC/USDT 1h 500개 수집 → parquet 저장 → 로드 성공, pytest 통과
다음 Phase 예고 : TA Learning Layer + Wave Decision Tree Engine
```

---

## 시스템 아키텍처 (6레이어)

```
Layer 1  DATA          ccxt + WebSocket → OHLCV 수집/저장
Layer 2  TA LEARNING   Text+Image → JSON → SQLite knowledge base
Layer 3  GROUNDING     JSON 패턴 → 실시간 피보나치 레벨 계산
Layer 4  WAVE TREE     이진 의사결정트리 → 시나리오 탐지
Layer 5  SIGNAL        시나리오 + 패턴 매칭 → SignalPacket
Layer 6  EXECUTOR      Binance Futures: Entry + SL + TP 주문
```

---

## 기술 스택

```
Language    : Python 3.11+
Exchange    : ccxt (Binance Futures)
Data Store  : parquet (OHLCV) + SQLite (knowledge base)
LLM         : Claude API (text → JSON parsing)
Infra       : Mac Mini M4 로컬
```

---

## Phase 완료 시 행동 규칙

```
1. 즉시 실행 정지
2. /egp/reports/phase_[N]_report.md 생성 (6섹션 양식)
3. Chairman에게 보고 텍스트 출력 (텔레그램 대체)
4. Chairman 승인 대기
   - APPROVED  → 다음 Phase PHASE_[N+1].md 읽고 개시
   - REVISION  → 수정 사항 반영 후 재보고
   - HALT      → 전체 중단 후 대기
```

---

## Bootstrap 모드 — Claude Code 역할 대행

```
CSO → 아키텍처 방향 및 레이어 설계 검토
CRO → 파동 탐지 가정 리스크, 과최적화 플래그
COO → 구현 병목 파악 및 Phase 진행 관리
CNO → 모델 비용 최적화 (Claude API 사용 최소화)
CTO → 기술스택 적합성 검토 및 코드 구현
CPO → Phase 산출물 검증 (실제 동작 여부)
```

---

## EGP 임계점 (thresholds.yaml 참조)

```
MDD (최대 낙폭)      : 10% 초과 → 즉시 중단 보고
신호 실패율          : 20% 초과 → CRO 플래그
```

---

## 참조 문서

- `/egp/council/roles.yaml` — Council 역할 (Bootstrap 대행)
- `/egp/triggers/thresholds.yaml` — 임계점 조건
- `/egp/phases/PHASE_1.md` — 현재 Phase 상세
- `/docs/architecture.md` — 시스템 아키텍처
- `/docs/tech_stack.md` — 기술스택 결정

---

*EGP v4.0 (간소화) | pyq001 | Chairman: qy3R*
