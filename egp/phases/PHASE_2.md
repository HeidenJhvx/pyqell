# PHASE_2.md — pyq001
# EGP v4.0 | Phase 2: TA Learning Layer + Wave Decision Tree

---

## Phase 2 목표

1. TA Learning Layer: 사용자 텍스트+이미지 해석 → JSON 구조화 → SQLite 저장
2. Wave Decision Tree: 이진 의사결정트리로 Elliott Wave 시나리오 탐지

⚠️ **Wave Decision Tree 설계는 Phase 1 완료 후 Chairman과 별도 심층 협의 필요**
    (의사결정트리 구조, 조건 집합, 시나리오 카탈로그 확정 필요)

---

## 임계 지표

```
완료 조건 1: 텍스트 해석 → WaveAnnotation JSON 파싱 성공률 ≥ 90%
완료 조건 2: Wave Decision Tree traversal — 주어진 MarketState에서 시나리오 반환
완료 조건 3: knowledge base CRUD 정상 동작 확인
```

---

## 산출물 정의

- [ ] /src/learning/parser.py — Text → JSON (Claude API)
- [ ] /src/learning/ingester.py — 이미지+텍스트 → KB 저장
- [ ] /src/learning/knowledge_base.py — SQLite CRUD
- [ ] /src/learning/schemas.py — WaveAnnotation 데이터 구조
- [ ] /src/elliott/conditions.py — 이진 조건 함수
- [ ] /src/elliott/tree_nodes.py — WaveNode, WaveScenario
- [ ] /src/elliott/wave_tree.py — 트리 정의 + traversal
- [ ] /src/elliott/scenarios.py — 시나리오 카탈로그
- [ ] /tests/test_learning.py 통과
- [ ] /tests/test_elliott.py 통과

---

## 리스크

```
리스크 1: LLM 파싱 비결정성 (동일 텍스트 → 다른 JSON)
          대응: structured output (json_schema) 강제 + 검증 레이어

리스크 2: Wave 트리 과적합 (특정 시장 구조에만 작동)
          대응: 여러 시장 상태 테스트 케이스 작성

리스크 3: 복수 유효 시나리오 처리 복잡도
          대응: confidence score 부여 + 상위 N개만 활성화
```

---

## 다음 Phase 예고

Phase 3: Pattern Grounding + Signal Synthesis + Backtest

*EGP v4.0 | pyq001 | Phase 2*
