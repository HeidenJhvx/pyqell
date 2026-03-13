"""
OHLCV Preprocessor — 정규화, 결측치 처리, 갭 탐지
Layer 1: Data Layer
"""
import logging
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# 타임프레임 → 예상 간격 (분) 매핑 (CRO 리스크 3: 데이터 갭)
TF_MINUTES = {
    "1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30,
    "1h": 60, "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720,
    "1d": 1440, "3d": 4320, "1w": 10080,
}


def preprocess_ohlcv(
    df: pd.DataFrame,
    timeframe: str,
    fill_gaps: bool = False,
    drop_incomplete: bool = True,
) -> pd.DataFrame:
    """OHLCV 데이터 전처리.

    Args:
        df: raw OHLCV DataFrame (timestamp index, UTC)
        timeframe: 예) "1h"
        fill_gaps: True면 결측 구간을 forward-fill (CRO: 불가 시 제외)
        drop_incomplete: True면 마지막(진행 중) 캔들 제거

    Returns:
        정제된 DataFrame + gaps_info 속성 추가
    """
    if df.empty:
        return df

    df = df.copy()

    # 1. 중복 인덱스 제거
    n_before = len(df)
    df = df[~df.index.duplicated(keep="last")]
    if len(df) < n_before:
        logger.debug(f"Removed {n_before - len(df)} duplicate timestamps")

    # 2. 시간순 정렬
    df = df.sort_index()

    # 3. 결측치 탐지 (갭)
    gaps = _detect_gaps(df, timeframe)
    if gaps:
        logger.warning(f"Found {len(gaps)} gap(s) in data:")
        for g in gaps[:5]:  # 최대 5개만 로그
            logger.warning(f"  Gap: {g['start']} → {g['end']} ({g['missing']} candles)")

    # 4. NaN 처리
    nan_count = df[["open", "high", "low", "close", "volume"]].isna().sum().sum()
    if nan_count > 0:
        logger.warning(f"Found {nan_count} NaN values")
        if fill_gaps:
            df = df.ffill().bfill()
        else:
            df = df.dropna(subset=["open", "high", "low", "close"])

    # 5. OHLC 논리 검증 (high >= max(open,close), low <= min(open,close))
    invalid = (
        (df["high"] < df[["open", "close"]].max(axis=1)) |
        (df["low"] > df[["open", "close"]].min(axis=1))
    )
    if invalid.any():
        logger.warning(f"Dropping {invalid.sum()} candles with invalid OHLC")
        df = df[~invalid]

    # 6. 진행 중 캔들 제거 (마지막 캔들은 미완성일 수 있음)
    if drop_incomplete and len(df) > 0:
        df = df.iloc[:-1]

    # 갭 정보 메타데이터 첨부 (테스트/리포트 용)
    df.attrs["gaps"] = gaps
    df.attrs["timeframe"] = timeframe

    return df


def _detect_gaps(df: pd.DataFrame, timeframe: str) -> list[dict]:
    """예상 간격보다 큰 타임스탬프 갭 탐지."""
    if timeframe not in TF_MINUTES:
        return []

    expected_minutes = TF_MINUTES[timeframe]
    expected_delta = pd.Timedelta(minutes=expected_minutes)
    tolerance = expected_delta * 1.5  # 1.5배 이상이면 갭

    diffs = df.index.to_series().diff().dropna()
    gap_mask = diffs > tolerance

    gaps = []
    for ts, delta in diffs[gap_mask].items():
        prev_ts = ts - delta
        missing = int(delta / expected_delta) - 1
        gaps.append({"start": prev_ts, "end": ts, "missing": missing})

    return gaps


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """로그 수익률 및 일반 수익률 컬럼 추가."""
    df = df.copy()
    df["return"] = df["close"].pct_change()
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))
    return df


def normalize_volume(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """거래량 정규화 (rolling z-score)."""
    df = df.copy()
    vol_mean = df["volume"].rolling(window).mean()
    vol_std = df["volume"].rolling(window).std()
    df["volume_zscore"] = (df["volume"] - vol_mean) / (vol_std + 1e-10)
    return df
