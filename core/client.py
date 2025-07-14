import os
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self, testnet=False):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.session = None

        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"

    async def initialize(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def fetch_market_data(self, symbol):
        await self.initialize()
        url = f"{self.base_url}/fapi/v1/klines?symbol={symbol}&interval=1m&limit=100"
        async with self.session.get(url) as response:
            data = await response.json()
            return data

    async def get_top_volume_symbols(self, limit=20):
        await self.initialize()
        url = f"{self.base_url}/fapi/v1/ticker/24hr"
        async with self.session.get(url) as response:
            tickers = await response.json()
            sorted_tickers = sorted(tickers, key=lambda x: float(x["quoteVolume"]), reverse=True)
            symbols = [t["symbol"] for t in sorted_tickers if t["symbol"].endswith("USDT")]
            return symbols[:limit]

    async def fetch_ohlcv(self, symbol, timeframe="1h", limit=100):
        await self.initialize()
        url = f"{self.base_url}/fapi/v1/klines?symbol={symbol}&interval={timeframe}&limit={limit}"
        async with self.session.get(url) as response:
            data = await response.json()
            return [[int(d[0]), float(d[1]), float(d[2]), float(d[3]), float(d[4]), float(d[5])] for d in data]

    async def get_futures_price(self, symbol):
        await self.initialize()
        url = f"{self.base_url}/fapi/v1/ticker/price?symbol={symbol}"
        async with self.session.get(url) as response:
            ticker = await response.json()
            return float(ticker['price'])

    async def fetch_order_book(self, symbol, limit=5):
        await self.initialize()
        url = f"{self.base_url}/fapi/v1/depth"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logger.warning(f"[ORDERBOOK] Fehler beim Abruf Orderbook für {symbol}: HTTP {response.status}")
                return {"bids": [], "asks": []}
