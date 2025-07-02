# strategies/futures_ema_rsi.py

"""
EMA & RSI-basierte Futures-Strategie mit ATR-SL/TP
"""
import numpy as np
import pandas as pd
from utils.logger import logger
from utils.indicators import EMA, RSI, ATR

class EMARSI_Strategy:
def **init**(self, client, symbols, interval, leverage, risk\_per\_trade):
self.client = client
self.symbols = symbols
self.interval = interval
self.leverage = leverage
self.risk_per_trade = risk_per_trade

```
async def check_signal(self, symbol):
    data = await self.client.fetch_ohlcv(symbol, self.interval)
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])

    ema_fast = EMA(df['close'], period=10)
    ema_slow = EMA(df['close'], period=20)
    rsi = RSI(df['close'], period=14)

    if ema_fast.iloc[-1] > ema_slow.iloc[-1] and rsi.iloc[-1] < 30:
        logger.info(f"Long signal für {symbol}")
        return 'LONG'
    if ema_fast.iloc[-1] < ema_slow.iloc[-1] and rsi.iloc[-1] > 70:
        logger.info(f"Short signal für {symbol}")
        return 'SHORT'
    return None

async def execute_trade(self, symbol, signal):
    # Positionsgröße berechnen
    balance = await self.client.fetch_balance()
    available = balance['total']['USDC']
    amount = (available * self.risk_per_trade) / price  # Preis muss aus DataFrame
    side = 'buy' if signal == 'LONG' else 'sell'
    order = await self.client.create_order(symbol, side, amount)
    if order:
        logger.info(f"Order ausgeführt: {order}")
```
