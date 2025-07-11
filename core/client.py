# core/client.py — Version 1.0.2

import asyncio
import ccxt.async_support as ccxt
from binance import AsyncClient
from utils.logger import logger

class BinanceClient:
    def __init__(self, client: AsyncClient):
        self.client = client

    @classmethod
    async def create(cls, api_key: str, api_secret: str, testnet: bool = False):
        logger.info(f"🔌 Verbinde mit Binance (testnet={testnet})...")
        client = await AsyncClient.create(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        return cls(client)

    async def get_futures_price(self, symbol: str) -> float:
        ticker = await self.client.futures_symbol_ticker(symbol=symbol)
        return float(ticker["price"])

    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int = None, limit: int = None, until: int = None):
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })
        if since and until:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since)
            ohlcv = [c for c in ohlcv if c[0] <= until]
        else:
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        await exchange.close()
        return ohlcv

    async def futures_change_leverage(self, symbol: str, leverage: int):
        """
        Setzt das Leverage für ein Futures-Symbol.
        """
        try:
            result = await self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            logger.info(f"[LEVERAGE] {symbol}: Leverage wurde auf {leverage}x gesetzt. Antwort: {result}")
            return result
        except Exception as e:
            logger.error(f"[LEVERAGE] Fehler beim Setzen des Leverage für {symbol}: {e}")
            raise

    async def close(self):
        await self.client.close_connection()
