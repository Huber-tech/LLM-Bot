# utils/backtester.py — Version 1.0.2

import os
import asyncio
import csv
import math
from datetime import datetime
from statistics import mean, pstdev
from core.client import BinanceClient
from core.trade_executor import TradeExecutor
from strategies.indicators import EMA, RSI, ATR
from utils.logger import logger
from dotenv import load_dotenv


__version__ = "1.0.2"

class Backtester:
    def __init__(self, symbol: str, start: str, end: str,
                 granularity: str = '1h', initial_balance: float = 20.0):
        self.symbol = symbol
        self.start = start
        self.end = end
        self.granularity = granularity
        self.initial_balance = initial_balance
        self.client = None
        self.executor = None
        self.reset()

    def reset(self):
        self.balance = self.initial_balance
        self.pos = None
        self.trades = []
        self.equity_curve = [self.initial_balance]

    async def run(self):
        # Lade API-Konfig aus .env
        load_dotenv()
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        testnet = os.getenv("USE_TESTNET", "True").lower() == "true"

        # BinanceClient asynchron initialisieren
        self.client = await BinanceClient.create(api_key, api_secret, testnet)
        self.executor = TradeExecutor(self.client)

        logger.info(f"📊 Backtest für {self.symbol} gestartet…")
        ohlcv = await self.client.fetch_ohlcv(
            self.symbol, self.granularity,
            since=self._ts(self.start),
            until=self._ts(self.end)
        )

        for i in range(len(ohlcv)):
            ts, o, h, l, c, v = ohlcv[i]
            time = datetime.utcfromtimestamp(ts/1000)

            # Indikatoren berechnen
            window_ema = [row[4] for row in ohlcv[max(0, i-50):i+1]]
            window_rsi = [row[4] for row in ohlcv[max(0, i-15):i+1]]
            window_atr = ohlcv[max(0, i-15):i+1]
            ema = EMA(window_ema, period=20)[-1]
            rsi = RSI(window_rsi, period=14)[-1]
            atr = ATR(window_atr, period=14)[-1]

            # Entry-Signale
            if not self.pos:
                if c > ema and rsi < 30:
                    signal = 'BUY'
                elif c < ema and rsi > 70:
                    signal = 'SELL'
                else:
                    signal = None

                if signal:
                    qty = self.balance / c
                    res = await self.executor.execute_trade(
                        self.symbol, signal, qty,
                        atr_period=14, sl_multiplier=1.5, tp_multiplier=3.0,
                        martingale_factor=1.0, paper=True
                    )
                    self.pos = {
                        'entry_time': time,
                        'entry_price': res['entry_price'],
                        'sl': res['sl_price'],
                        'tp': res['tp_price'],
                        'qty': res['qty'],
                        'side': signal
                    }

            # Exit-Logik
            if self.pos:
                price = c
                side = self.pos['side']
                exit_trade = False
                if side == 'BUY' and (price <= self.pos['sl'] or price >= self.pos['tp']):
                    exit_trade = True
                elif side == 'SELL' and (price >= self.pos['sl'] or price <= self.pos['tp']):
                    exit_trade = True

                if exit_trade:
                    pnl = (price - self.pos['entry_price']) * self.pos['qty']
                    if side == 'SELL':
                        pnl *= -1
                    self.balance += pnl
                    self.trades.append({
                        'entry': self.pos['entry_price'],
                        'exit': price,
                        'pnl': pnl
                    })
                    self.equity_curve.append(self.balance)
                    logger.info(
                        f"[Backtest] {side} {self.symbol} Entry={self.pos['entry_price']:.2f} Exit={price:.2f} P&L={pnl:.4f} Bal={self.balance:.4f}"
                    )
                    self.pos = None

        stats = self._compute_metrics()
        self._save_results(stats)
        logger.info(f"📈 Backtest abgeschlossen — Endbalance: {self.balance:.2f} — Stats: {stats}")

    def _compute_metrics(self):
        returns = []
        peak = self.initial_balance
        max_dd = 0
        wins = 0

        for bal in self.equity_curve[1:]:
            ret = (bal - peak) / peak
            returns.append(ret)
            if bal > peak:
                peak = bal
            dd = (peak - bal) / peak
            max_dd = max(max_dd, dd)
            if ret > 0:
                wins += 1

        win_rate = wins / len(returns) if returns else 0
        avg_ret = mean(returns) if returns else 0
        std_ret = pstdev(returns) if len(returns) > 1 else 0.0001
        sharpe = (avg_ret / std_ret) * math.sqrt(8760) if std_ret else 0
        total_return = (self.balance - self.initial_balance) / self.initial_balance

        return {
            'total_return': total_return,
            'max_drawdown': max_dd,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe
        }

    def _save_results(self, stats: dict):
        base = f"backtest_{self.symbol}_{self.start}_{self.end}"
        with open(f"{base}.csv", 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['entry', 'exit', 'pnl'])
            writer.writeheader()
            for t in self.trades:
                writer.writerow(t)
        with open(f"{base}_stats.txt", 'w') as f:
            for k, v in stats.items():
                f.write(f"{k}: {v}\n")

    @staticmethod
    def _ts(date_str: str) -> int:
        dt = datetime.fromisoformat(date_str)
        return int(dt.timestamp() * 1000)
