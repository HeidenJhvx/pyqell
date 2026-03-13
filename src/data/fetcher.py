"""
OHLCV Fetcher — ccxt 기반 Binance 데이터 수집
Layer 1: Data Layer
"""
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Optional

import ccxt
import ccxt.async_support as ccxt_async
import pandas as pd

logger = logging.getLogger(__name__)


class OHLCVFetcher:
    """ccxt 기반 OHLCV 데이터 수집기."""

    # Binance API 레이트 리밋 대응 (CRO 리스크 1)
    REQUEST_DELAY_MS = 200
    MAX_CANDLES_PER_REQUEST = 1000

    def __init__(self, exchange_id: str = "binance", testnet: bool = False):
        self.exchange_id = exchange_id
        self.testnet = testnet
        self._exchange: Optional[ccxt.Exchange] = None

    def _get_exchange(self) -> ccxt.Exchange:
        if self._exchange is None:
            exchange_class = getattr(ccxt, self.exchange_id)
            options = {"defaultType": "future"} if self.exchange_id == "binance" else {}
            self._exchange = exchange_class({"options": options})
            if self.testnet and hasattr(self._exchange, "set_sandbox_mode"):
                self._exchange.set_sandbox_mode(True)
        return self._exchange

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since: Optional[datetime] = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        """OHLCV 동기 수집.

        Args:
            symbol: 예) "BTC/USDT"
            timeframe: 예) "1h", "4h", "1d"
            since: 시작 시각 (None이면 최신 limit개)
            limit: 최대 캔들 수

        Returns:
            DataFrame (timestamp, open, high, low, close, volume)
        """
        exchange = self._get_exchange()
        since_ms = int(since.timestamp() * 1000) if since else None

        all_candles = []
        fetched = 0

        while fetched < limit:
            batch = min(self.MAX_CANDLES_PER_REQUEST, limit - fetched)
            try:
                candles = exchange.fetch_ohlcv(
                    symbol,
                    timeframe=timeframe,
                    since=since_ms,
                    limit=batch,
                )
            except ccxt.RateLimitExceeded:
                logger.warning("Rate limit exceeded, waiting 1s...")
                time.sleep(1)
                continue
            except ccxt.NetworkError as e:
                logger.error(f"Network error fetching {symbol} {timeframe}: {e}")
                raise

            if not candles:
                break

            all_candles.extend(candles)
            fetched += len(candles)

            if len(candles) < batch:
                break

            # 다음 요청 시작점을 마지막 캔들 이후로
            since_ms = candles[-1][0] + 1
            time.sleep(self.REQUEST_DELAY_MS / 1000)

        return self._to_dataframe(all_candles)

    def fetch_multi_timeframe(
        self,
        symbol: str,
        timeframes: list[str],
        limit: int = 500,
    ) -> dict[str, pd.DataFrame]:
        """멀티 타임프레임 동시 수집."""
        result = {}
        for tf in timeframes:
            logger.info(f"Fetching {symbol} {tf}...")
            result[tf] = self.fetch_ohlcv(symbol, tf, limit=limit)
        return result

    async def fetch_ohlcv_async(
        self,
        symbol: str,
        timeframe: str,
        since: Optional[datetime] = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        """OHLCV 비동기 수집."""
        exchange_class = getattr(ccxt_async, self.exchange_id)
        exchange = exchange_class({"options": {"defaultType": "future"}})
        if self.testnet and hasattr(exchange, "set_sandbox_mode"):
            exchange.set_sandbox_mode(True)

        try:
            since_ms = int(since.timestamp() * 1000) if since else None
            all_candles = []
            fetched = 0

            while fetched < limit:
                batch = min(self.MAX_CANDLES_PER_REQUEST, limit - fetched)
                try:
                    candles = await exchange.fetch_ohlcv(
                        symbol, timeframe=timeframe, since=since_ms, limit=batch
                    )
                except ccxt.RateLimitExceeded:
                    await asyncio.sleep(1)
                    continue

                if not candles:
                    break

                all_candles.extend(candles)
                fetched += len(candles)

                if len(candles) < batch:
                    break

                since_ms = candles[-1][0] + 1
                await asyncio.sleep(self.REQUEST_DELAY_MS / 1000)

            return self._to_dataframe(all_candles)
        finally:
            await exchange.close()

    def _to_dataframe(self, candles: list) -> pd.DataFrame:
        """ccxt 캔들 리스트 → pandas DataFrame 변환."""
        if not candles:
            return pd.DataFrame(
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )

        df = pd.DataFrame(
            candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
        # timestamp: ms → UTC datetime (CRO 리스크 2: 타임존 UTC 통일)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df = df.set_index("timestamp")
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        df = df.sort_index()
        return df

    def close(self):
        if self._exchange:
            self._exchange.close()
            self._exchange = None
