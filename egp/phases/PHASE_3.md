# PHASE_3.md — pyq001
# EGP v4.0 | Phase 3: Grounding + Signal + Backtest

---

## Phase 3 목표

1. Pattern Grounding: KB 패턴 → 실시간 피보나치 레벨 동적 계산
2. Signal Synthesis: Wave 시나리오 + 패턴 매칭 → SignalPacket 생성
3. Backtest: 과거 데이터로 신호 성과 검증

---

## 임계 지표

```
완료 조건 1: 최근 1년 BTC/USDT 1h 백테스트 실행 완료
완료 조건 2: Sharpe Ratio > 0.5 (연율화)
완료 조건 3: 신호 실패율 < 20% (EGP threshold)
완료 조건 4: 최대 낙폭(MDD) < 20% (백테스트 기준)
```

---

## 산출물 정의

- [ ] /src/grounding/swing_detector.py
- [ ] /src/grounding/fibonacci.py
- [ ] /src/grounding/matcher.py
- [ ] /src/signals/synthesizer.py
- [ ] /src/signals/risk_calc.py
- [ ] /src/signals/validator.py
- [ ] /src/risk/position_sizer.py
- [ ] /src/risk/stop_manager.py
- [ ] /src/backtest/engine.py
- [ ] /docs/backtest_report.md (백테스트 결과)
- [ ] /tests/test_signals.py 통과

---

## 리스크

```
리스크 1: 백테스트 과최적화 (in-sample 과적합)
          대응: Walk-forward validation, out-of-sample 테스트 분리

리스크 2: 신호 희소성 (Wave 조건이 너무 엄격해 신호 거의 없음)
          대응: confidence threshold 조정, 최소 신호 수 기준 설정

리스크 3: 슬리피지/수수료 미반영
          대응: 백테스트에 Binance 수수료(0.04%) + 슬리피지(0.05%) 반영
```

---

## 다음 Phase 예고

Phase 4: Binance Testnet 페이퍼 트레이딩

*EGP v4.0 | pyq001 | Phase 3*
