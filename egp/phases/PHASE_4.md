# PHASE_4.md — pyq001
# EGP v4.0 | Phase 4: Paper Trading → Live Preparation

---

## Phase 4 목표

Binance Futures Testnet에서 페이퍼 트레이딩 실행.
실거래 전환 전 시스템 안정성 + 리스크 관리 검증.

---

## 임계 지표

```
완료 조건 1: Testnet 페이퍼 트레이딩 7일 이상 무중단 실행
완료 조건 2: MDD < 10% (EGP 임계점 이내)
완료 조건 3: 신호 → 주문 → SL/TP 설정까지 전 사이클 자동화 확인
완료 조건 4: 주문 실패 시 재시도/롤백 로직 검증
```

---

## 산출물 정의

- [ ] /src/executor/paper.py — 페이퍼 트레이딩 시뮬레이터
- [ ] /src/executor/binance_futures.py — ccxt Binance Futures wrapper
- [ ] /src/executor/order_manager.py — Entry + SL + TP 원자적 실행
- [ ] /src/executor/position_monitor.py — 포지션 추적
- [ ] /docs/paper_trading_report.md (결과 보고)

---

## 리스크

```
리스크 1: Testnet 가격이 실제와 다를 수 있음
          대응: 결과 참고용으로만 활용, 슬리피지 추가 보수적 반영

리스크 2: 주문 원자성 실패 (Entry 성공 후 SL 실패)
          대응: Entry 확인 후 SL 설정, 실패 시 즉시 Entry 취소

리스크 3: WebSocket 연결 끊김 시 미관리 포지션
          대응: 재연결 로직 + 포지션 상태 복구 메커니즘
```

---

## 실거래 전환 조건 (Chairman 승인 필요)

- 페이퍼 7일 이상 MDD < 10% 유지
- 신호 실패율 < 20% 유지
- Chairman이 실거래 전환 승인 (`/approve`)

---

## 다음 Phase 예고

Phase 5: Binance Futures 실거래 + EGP 임계점 모니터링

*EGP v4.0 | pyq001 | Phase 4*
