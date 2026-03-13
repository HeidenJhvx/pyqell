"""
OHLCV Stream — Binance WebSocket 실시간 캔들 스트림
Layer 1: Data Layer (Phase 3에서 완성)

현재: 기본 구조 + 인터페이스 정의
"""
import asyncio
import json
import logging
from typing import Callable, Optional

import websockets
import pandas as pd

logger = logging.getLogger(__name__)

# Binance WebSocket URL
BINANCE_WS_BASE = "wss://fstream.binance.com/ws"
BINANCE_WS_TESTNET = "wss://stream.binancefuture.com/ws"


class CandleStream:
    """Binance Futures WebSocket 실시간 캔들 스트림.

    Phase 3에서 완성. 현재는 기본 구조.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        on_candle: Callable[[pd.Series], None],
        testnet: bool = True,
    ):
        """
        Args:
            symbol: 예) "BTC/USDT" → "btcusdt"로 변환
            timeframe: 예) "1h"
            on_candle: 완성된 캔들 수신 시 콜백
            testnet: True면 Testnet WebSocket 사용
        """
        self.symbol = symbol.replace("/", "").lower()
        self.timeframe = timeframe
        self.on_candle = on_candle
        self.ws_base = BINANCE_WS_TESTNET if testnet else BINANCE_WS_BASE
        self._running = False
        self._ws = None

    @property
    def stream_url(self) -> str:
        return f"{self.ws_base}/{self.symbol}@kline_{self.timeframe}"

    async def start(self):
        """WebSocket 스트림 시작 (재연결 포함)."""
        self._running = True
        while self._running:
            try:
                await self._connect()
            except Exception as e:
                logger.error(f"Stream error ({self.symbol} {self.timeframe}): {e}")
                if self._running:
                    logger.info("Reconnecting in 5s...")
                    await asyncio.sleep(5)

    async def stop(self):
        self._running = False
        if self._ws:
            await self._ws.close()

    async def _connect(self):
        logger.info(f"Connecting to {self.stream_url}")
        async with websockets.connect(self.stream_url) as ws:
            self._ws = ws
            async for message in ws:
                if not self._running:
                    break
                await self._handle_message(message)

    async def _handle_message(self, message: str):
        data = json.loads(message)
        kline = data.get("k", {})

        # 캔들이 완성된 경우만 처리 (x: true = closed candle)
        if kline.get("x"):
            candle = pd.Series(
                {
                    "open": float(kline["o"]),
                    "high": float(kline["h"]),
                    "low": float(kline["l"]),
                    "close": float(kline["c"]),
                    "volume": float(kline["v"]),
                },
                name=pd.Timestamp(kline["t"], unit="ms", tz="UTC"),
            )
            self.on_candle(candle)
