"""
Phase 1 완료 조건 검증 테스트
- ccxt OHLCV 수집 성공
- parquet 저장/로드 무결성
- preprocessor 정상 동작
"""
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

from src.data.fetcher import OHLCVFetcher
from src.data.storage import OHLCVStorage
from src.data.preprocessor import preprocess_ohlcv, _detect_gaps


# ── Storage 단위 테스트 ───────────────────────────────────────────

class TestOHLCVStorage:
    """parquet 저장/로드 테스트 (네트워크 불필요)."""

    def _make_df(self, n: int = 100, start: str = "2024-01-01") -> pd.DataFrame:
        idx = pd.date_range(start, periods=n, freq="1h", tz="UTC")
        return pd.DataFrame(
            {
                "open":   100.0 + pd.Series(range(n)).values,
                "high":   101.0 + pd.Series(range(n)).values,
                "low":     99.0 + pd.Series(range(n)).values,
                "close":  100.5 + pd.Series(range(n)).values,
                "volume":  1000.0 + pd.Series(range(n)).values,
            },
            index=idx,
        )

    def test_save_and_load(self, tmp_path):
        storage = OHLCVStorage(base_dir=str(tmp_path))
        df = self._make_df(100)

        path = storage.save(df, "BTC/USDT", "1h")
        assert path.exists()

        loaded = storage.load("BTC/USDT", "1h")
        assert len(loaded) == 100
        assert list(loaded.columns) == ["open", "high", "low", "close", "volume"]

    def test_merge_on_save(self, tmp_path):
        """기존 데이터에 신규 데이터 추가 시 중복 제거 확인."""
        storage = OHLCVStorage(base_dir=str(tmp_path))
        df1 = self._make_df(100, "2024-01-01")
        df2 = self._make_df(50, "2024-01-05")  # df1과 일부 겹침

        storage.save(df1, "BTC/USDT", "1h")
        storage.save(df2, "BTC/USDT", "1h")

        loaded = storage.load("BTC/USDT", "1h")
        assert loaded.index.is_monotonic_increasing
        assert not loaded.index.duplicated().any()

    def test_integrity_check(self, tmp_path):
        storage = OHLCVStorage(base_dir=str(tmp_path))
        df = self._make_df(50)
        storage.save(df, "ETH/USDT", "4h")
        assert storage.verify_integrity("ETH/USDT", "4h") is True

    def test_load_with_filter(self, tmp_path):
        storage = OHLCVStorage(base_dir=str(tmp_path))
        df = self._make_df(200, "2024-01-01")
        storage.save(df, "BTC/USDT", "1h")

        start = pd.Timestamp("2024-01-05", tz="UTC")
        loaded = storage.load("BTC/USDT", "1h", start=start)
        assert (loaded.index >= start).all()

    def test_info(self, tmp_path):
        storage = OHLCVStorage(base_dir=str(tmp_path))
        df = self._make_df(100)
        storage.save(df, "BTC/USDT", "1h")
        info = storage.info("BTC/USDT", "1h")
        assert info["exists"] is True
        assert info["count"] == 100

    def test_not_exists(self, tmp_path):
        storage = OHLCVStorage(base_dir=str(tmp_path))
        assert storage.exists("XYZ/USDT", "1h") is False
        assert storage.verify_integrity("XYZ/USDT", "1h") is False


# ── Preprocessor 단위 테스트 ──────────────────────────────────────

class TestPreprocessor:

    def _make_df(self, n: int = 100, freq: str = "1h") -> pd.DataFrame:
        idx = pd.date_range("2024-01-01", periods=n, freq=freq, tz="UTC")
        return pd.DataFrame(
            {
                "open":   [100.0] * n,
                "high":   [101.0] * n,
                "low":    [99.0] * n,
                "close":  [100.5] * n,
                "volume": [1000.0] * n,
            },
            index=idx,
        )

    def test_basic_preprocess(self):
        df = self._make_df(100)
        result = preprocess_ohlcv(df, "1h")
        assert len(result) == 99  # drop_incomplete=True → 마지막 1개 제거
        assert result.index.is_monotonic_increasing

    def test_no_duplicate_index(self):
        df = self._make_df(10)
        # 중복 인덱스 삽입
        df_dup = pd.concat([df, df.iloc[:3]])
        result = preprocess_ohlcv(df_dup, "1h")
        assert not result.index.duplicated().any()

    def test_detect_gaps(self):
        idx = pd.date_range("2024-01-01", periods=50, freq="1h", tz="UTC")
        # 중간에 5시간 갭 삽입
        idx2 = pd.date_range("2024-01-03 12:00", periods=50, freq="1h", tz="UTC")
        combined_idx = idx.append(idx2)
        df = pd.DataFrame(
            {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
            index=combined_idx,
        )
        gaps = _detect_gaps(df, "1h")
        assert len(gaps) >= 1

    def test_invalid_ohlc_dropped(self):
        df = self._make_df(10)
        # 1개 행의 high를 close보다 낮게 만들어 유효하지 않게
        df.iloc[5, df.columns.get_loc("high")] = 99.0  # high < close (100.5)
        result = preprocess_ohlcv(df, "1h", drop_incomplete=False)
        assert len(result) == 9  # 1개 제거


# ── 통합 테스트: 실제 ccxt 수집 + 저장 (네트워크 필요) ─────────────

@pytest.mark.integration
class TestFetchAndStore:
    """실제 Binance API 수집 테스트.

    네트워크 연결 필요. --integration 플래그로 실행:
    pytest tests/test_data.py -m integration
    """

    def test_fetch_btc_1h(self, tmp_path):
        fetcher = OHLCVFetcher(exchange_id="binance", testnet=False)
        try:
            df = fetcher.fetch_ohlcv("BTC/USDT", "1h", limit=100)
            assert len(df) >= 100
            assert list(df.columns) == ["open", "high", "low", "close", "volume"]
            assert df.index.tz is not None  # UTC timestamp
            assert df.index.is_monotonic_increasing
        finally:
            fetcher.close()

    def test_fetch_and_save(self, tmp_path):
        fetcher = OHLCVFetcher(exchange_id="binance", testnet=False)
        storage = OHLCVStorage(base_dir=str(tmp_path))
        try:
            df = fetcher.fetch_ohlcv("BTC/USDT", "1h", limit=500)
            processed = preprocess_ohlcv(df, "1h")
            storage.save(processed, "BTC/USDT", "1h")

            loaded = storage.load("BTC/USDT", "1h")
            assert len(loaded) >= 499  # drop_incomplete로 1개 제거
            assert storage.verify_integrity("BTC/USDT", "1h")
        finally:
            fetcher.close()

    def test_multi_timeframe(self, tmp_path):
        fetcher = OHLCVFetcher(exchange_id="binance", testnet=False)
        storage = OHLCVStorage(base_dir=str(tmp_path))
        try:
            timeframes = ["1h", "4h", "1d"]
            data = fetcher.fetch_multi_timeframe("BTC/USDT", timeframes, limit=100)

            for tf in timeframes:
                assert tf in data
                assert len(data[tf]) > 0
                storage.save(data[tf], "BTC/USDT", tf)
                assert storage.exists("BTC/USDT", tf)
        finally:
            fetcher.close()
