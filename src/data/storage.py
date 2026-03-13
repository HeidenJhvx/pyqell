"""
OHLCV Storage — parquet 기반 로컬 저장/로드
Layer 1: Data Layer
"""
import hashlib
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class OHLCVStorage:
    """parquet 기반 OHLCV 로컬 저장소.

    파일 경로: {base_dir}/{exchange}/{symbol_safe}/{timeframe}.parquet
    예)  src/data/parquet/binance/BTC_USDT/1h.parquet
    """

    def __init__(self, base_dir: str = "src/data/parquet"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, symbol: str, timeframe: str, exchange: str = "binance") -> Path:
        symbol_safe = symbol.replace("/", "_")
        return self.base_dir / exchange / symbol_safe / f"{timeframe}.parquet"

    def save(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        exchange: str = "binance",
    ) -> Path:
        """DataFrame을 parquet으로 저장.

        기존 데이터가 있으면 중복 제거 후 머지.
        """
        path = self._path(symbol, timeframe, exchange)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            existing = self._load_raw(path)
            df = pd.concat([existing, df])
            df = df[~df.index.duplicated(keep="last")]
            df = df.sort_index()

        df.to_parquet(path, engine="pyarrow", compression="snappy")
        logger.info(f"Saved {len(df)} candles → {path}")
        return path

    def load(
        self,
        symbol: str,
        timeframe: str,
        exchange: str = "binance",
        start: pd.Timestamp = None,
        end: pd.Timestamp = None,
    ) -> pd.DataFrame:
        """parquet에서 OHLCV 로드.

        Args:
            start: 시작 시각 필터 (None이면 전체)
            end:   종료 시각 필터 (None이면 전체)
        """
        path = self._path(symbol, timeframe, exchange)
        if not path.exists():
            logger.warning(f"No data file: {path}")
            return pd.DataFrame(
                columns=["open", "high", "low", "close", "volume"]
            )

        df = self._load_raw(path)

        if start is not None:
            df = df[df.index >= start]
        if end is not None:
            df = df[df.index <= end]

        return df

    def exists(self, symbol: str, timeframe: str, exchange: str = "binance") -> bool:
        return self._path(symbol, timeframe, exchange).exists()

    def info(self, symbol: str, timeframe: str, exchange: str = "binance") -> dict:
        """저장된 데이터 메타정보 반환."""
        path = self._path(symbol, timeframe, exchange)
        if not path.exists():
            return {"exists": False}

        df = self._load_raw(path)
        return {
            "exists": True,
            "path": str(path),
            "count": len(df),
            "start": str(df.index.min()),
            "end": str(df.index.max()),
            "size_kb": round(path.stat().st_size / 1024, 1),
        }

    def verify_integrity(self, symbol: str, timeframe: str, exchange: str = "binance") -> bool:
        """저장된 parquet 파일 무결성 검증 (CRO 리스크 4)."""
        path = self._path(symbol, timeframe, exchange)
        if not path.exists():
            return False
        try:
            df = self._load_raw(path)
            assert len(df) > 0
            assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"])
            assert df.index.is_monotonic_increasing
            return True
        except Exception as e:
            logger.error(f"Integrity check failed for {path}: {e}")
            return False

    def _load_raw(self, path: Path) -> pd.DataFrame:
        return pd.read_parquet(path, engine="pyarrow")
