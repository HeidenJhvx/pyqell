# Wave Decision Tree Spec — pyq001
# ⚠️ Phase 2 시작 전 Chairman과 심층 협의 필요

---

## 현재 상태

이 문서는 Phase 2 설계 세션 전 **프레임 정의**만 포함.
구체적인 트리 구조, 조건 집합, 시나리오 카탈로그는 Chairman과 협의 후 확정.

---

## 핵심 설계 이슈 (협의 필요 항목)

### Issue 1: 의사결정트리 분기 기준

**옵션 A**: 파동 규칙 조건만 사용 (순수 Elliott Wave 3대 규칙)
```
- W2는 W1의 100%를 되돌릴 수 없다
- W3는 3개 임펄스 파동 중 가장 짧을 수 없다
- W4는 W1 영역과 겹칠 수 없다
```

**옵션 B**: 파동 규칙 + Fibonacci 레벨 조건 복합
```
- W2 되돌림이 38.2%~61.8% 구간인가? (황금 되돌림)
- W3 길이가 W1의 161.8% 이상인가?
```

**옵션 C**: 파동 규칙 + Fibonacci + 보조 지표 확인
```
- 위 조건 + RSI divergence 확인
- 위 조건 + Volume 확인
```

→ **협의 필요**: 어느 옵션이 시스템 설계 철학과 맞는가?

---

### Issue 2: 복수 유효 시나리오 처리

동일 시점에 여러 유효한 파동 카운트가 존재할 수 있음.

**옵션 A**: 단일 최선 시나리오 (confidence 최고)
**옵션 B**: 상위 N개 시나리오 동시 추적 (N=2~3)
**옵션 C**: 모든 유효 시나리오 추적 + confidence 가중

→ **협의 필요**: 트레이딩 실행은 단일 신호만? 복수 신호 허용?

---

### Issue 3: 실시간 vs 확정 파동 구분

파동은 완료 후에야 확정. 진행 중인 파동은 가설.

**현재 접근**:
- "현재 W3 진행 중" = 확정된 W1, W2 이후 + 가격이 특정 조건 만족
- 무효화 레벨(SL) = W2 저점 (롱 기준) → W2 아래로 내려가면 시나리오 무효

**협의 필요**:
- W1, W2 확정 기준 (캔들 수? 가격 비율?)
- ZigZag 감도 파라미터 (config에 5%로 설정됨 — 적절한가?)

---

### Issue 4: 파동 차수 (Degree)

어느 차수에서 카운팅할 것인가?

```
Supercycle  (수년)
Cycle       (수개월)
Primary     (수주)        ← 1d 차트 기준
Intermediate (수일)       ← 4h 차트 기준
Minor        (수시간)     ← 1h 차트 기준 (현재 설정)
Minute       (수십분)     ← 15m 차트
```

**현재 설정**: 1h 차트를 주 차트로 사용 (Minor 차수).
1d/4h는 상위 차수 필터 역할.

**협의 필요**: 이 차수 선택이 맞는가?

---

## 시나리오 카탈로그 (초안)

Phase 2 협의 후 확정될 시나리오 목록 (현재는 예시):

### 임펄스 파동 시나리오
```
W1_IMPULSE_BULL   : 1파 상승 진행 중 (LONG)
W2_CORRECTION     : 2파 되돌림 대기 (WAIT / 롱 준비)
W3_IMPULSE_BULL   : 3파 상승 진행 중 (LONG — 핵심 진입)
W4_CORRECTION     : 4파 되돌림 대기 (WAIT)
W5_IMPULSE_BULL   : 5파 상승 진행 중 (LONG — 주의, 곧 반전)

W1_IMPULSE_BEAR   : 1파 하락 진행 (SHORT)
W3_IMPULSE_BEAR   : 3파 하락 진행 (SHORT — 핵심 진입)
```

### 조정 파동 시나리오
```
WA_CORRECTION     : A파 하락 (기존 롱 청산 구간)
WB_CORRECTION     : B파 반등 (숏 진입 준비)
WC_CORRECTION     : C파 하락 (SHORT)
```

### 불확실 시나리오
```
UNDEFINED         : 파동 구조 불명확 (WAIT)
AMBIGUOUS         : 복수 카운트 충돌 (최소 포지션 또는 WAIT)
```

---

## 기술 구조 (확정)

```python
from dataclasses import dataclass
from typing import Callable, Union

@dataclass
class MarketState:
    symbol: str
    timeframe: str
    current_price: float
    swings: list           # ZigZag 스윙 포인트 목록
    current_candle: dict   # OHLCV

@dataclass
class WaveScenario:
    name: str
    signal_type: str       # LONG / SHORT / WAIT
    confidence: float      # 0.0 ~ 1.0
    invalidation_fn: Callable[[MarketState], float]  # → SL 가격
    target_fn: Callable[[MarketState], list]         # → [TP1, TP2, ...]

class WaveNode:
    def __init__(
        self,
        condition: Callable[[MarketState], bool],
        true_branch: Union['WaveNode', WaveScenario],
        false_branch: Union['WaveNode', WaveScenario],
    ): ...

    def evaluate(self, state: MarketState) -> WaveScenario:
        if self.condition(state):
            return self.true_branch.evaluate(state)
        else:
            return self.false_branch.evaluate(state)
```

---

*이 문서는 Phase 2 협의 세션에서 업데이트됩니다.*
*EGP v4.0 | pyq001 | Wave Spec v0.1 (Draft)*
