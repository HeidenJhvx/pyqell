# pyq001 — System Architecture
# Elliott Wave TA Quant System

---

## 전체 아키텍처 (6레이어)

```
┌─────────────────────────────────────────────────────────────────┐
│                    pyq001 Architecture                           │
├──────────────────────────────────────────────────────────────── ┤
│  Layer 1: DATA LAYER                                            │
│  ─────────────────────────────────────────────────────────────  │
│  ccxt (Binance) → OHLCV 수집 → parquet 저장                      │
│  WebSocket → 실시간 캔들 스트림 (Phase 3+)                        │
│  타임프레임: 1d / 4h / 1h / 15m (멀티 TF)                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: TA LEARNING LAYER                                     │
│  ─────────────────────────────────────────────────────────────  │
│  Input:  사용자 텍스트 해석 + 차트 이미지(optional)               │
│  Parse:  Claude API → WaveAnnotation JSON                       │
│  Store:  SQLite knowledge_base (패턴 DB)                         │
│                                                                  │
│  WaveAnnotation:                                                 │
│    symbol, timeframe, wave_position, direction                   │
│    key_levels(origin, w1_end, w2_end, invalidation)             │
│    fibonacci(retracement, target_ext), tp_targets               │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: PATTERN GROUNDING                                     │
│  ─────────────────────────────────────────────────────────────  │
│  ZigZag → 현재 스윙 하이/로우 탐지                                │
│  KB 패턴 → 현재 스윙 기준으로 피보나치 레벨 동적 재계산            │
│  Matcher → 현재 시장 상태 vs KB 패턴 유사도 점수                   │
│  (정적 가격 아닌 동적 비율 기반 레벨)                              │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: WAVE DECISION TREE ENGINE (이진 의사결정트리)          │
│  ─────────────────────────────────────────────────────────────  │
│  각 노드: Callable[[MarketState], bool]                           │
│  True/False 분기 → 하위 노드 또는 리프(WaveScenario)             │
│                                                                  │
│  예시 트리 경로:                                                  │
│  "임펄스 구조 존재?" → YES                                        │
│    → "W1 완료?" → YES                                            │
│      → "W2 완료?" → YES                                          │
│        → "현재가 > W1 고점?" → YES                               │
│          → WaveScenario("W3_IMPULSE_BULL")                      │
│                                                                  │
│  WaveScenario:                                                   │
│    name, signal_type, invalidation_fn, target_fn, confidence    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5: SIGNAL SYNTHESIS                                      │
│  ─────────────────────────────────────────────────────────────  │
│  Wave Scenario + Pattern Match Score → SignalPacket             │
│                                                                  │
│  SignalPacket:                                                   │
│    symbol, direction(LONG/SHORT), entry_price                   │
│    sl_price (파동 무효화 레벨), tp_prices (피보나치 목표)          │
│    leverage (리스크 기반 계산), position_size_pct                │
│    scenario, confidence                                          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 6: EXECUTOR (Binance Futures)                            │
│  ─────────────────────────────────────────────────────────────  │
│  Phase 4: Paper Trading (Testnet)                               │
│  Phase 5: Live Trading                                           │
│                                                                  │
│  실행 순서:                                                       │
│    1. set_leverage(leverage)                                     │
│    2. market_order(direction, size)   ← Entry                   │
│    3. stop_market_order(sl_price)     ← Stop Loss               │
│    4. limit_order(tp_prices)          ← Take Profit             │
├─────────────────────────────────────────────────────────────────┤
│  EGP GOVERNANCE LAYER                                           │
│  ─────────────────────────────────────────────────────────────  │
│  Phase Gate: 완료 감지 → 보고서 → Chairman 승인                  │
│  Threshold Monitor: MDD 10% / 신호실패 20%                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 데이터 흐름

```
사용자 TA 해석 텍스트
        ↓
  Layer 2: Claude API 파싱
        ↓
  SQLite Knowledge Base
        ↑         ↓
  Layer 3: ZigZag 스윙 탐지 → 피보나치 동적 계산 → 패턴 매칭
        ↓
  Layer 4: Wave Decision Tree → 활성 시나리오 목록
        ↓
  Layer 5: Signal Synthesis → SignalPacket
        ↓
  Layer 6: Executor → Binance Futures 주문
        ↓
  포지션 모니터링 → SL/TP 히트 → 청산
```

---

## 멀티 타임프레임 전략

```
1d  : 대파동 방향 확인 (트렌드 필터)
4h  : 중기 파동 구조 확인 (시나리오 탐지)
1h  : 진입 타이밍 (Wave Decision Tree 주 동작)
15m : 세밀 진입 최적화 (optional)
```

원칙: 상위 TF 방향과 일치하는 하위 TF 신호만 진입

---

## 파일 구조

```
pyq001/
├── CLAUDE.md                    ← EGP 헤더
├── config/config.yaml           ← 전체 설정
├── src/
│   ├── data/                    ← Layer 1
│   │   ├── fetcher.py
│   │   ├── stream.py
│   │   ├── storage.py
│   │   └── preprocessor.py
│   ├── learning/                ← Layer 2
│   │   ├── parser.py
│   │   ├── ingester.py
│   │   ├── knowledge_base.py
│   │   └── schemas.py
│   ├── grounding/               ← Layer 3
│   │   ├── swing_detector.py
│   │   ├── fibonacci.py
│   │   └── matcher.py
│   ├── elliott/                 ← Layer 4
│   │   ├── conditions.py
│   │   ├── tree_nodes.py
│   │   ├── wave_tree.py
│   │   └── scenarios.py
│   ├── signals/                 ← Layer 5
│   │   ├── synthesizer.py
│   │   ├── risk_calc.py
│   │   └── validator.py
│   ├── risk/
│   │   ├── position_sizer.py
│   │   └── stop_manager.py
│   ├── backtest/                ← Phase 3
│   │   └── engine.py
│   └── executor/                ← Layer 6
│       ├── paper.py
│       ├── binance_futures.py
│       ├── order_manager.py
│       └── position_monitor.py
├── docs/
│   ├── architecture.md          ← 이 문서
│   ├── tech_stack.md
│   └── wave_decision_tree_spec.md  ← Phase 2 전 협의
├── egp/                         ← EGP 거버넌스
│   ├── council/roles.yaml
│   ├── triggers/thresholds.yaml
│   ├── phases/PHASE_1~5.md
│   └── reports/
└── tests/
```
