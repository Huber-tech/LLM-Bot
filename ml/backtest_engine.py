import argparse
import pandas as pd
import ccxt
import os
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from strategies.engine import StrategyEngine
from strategies.rsi_ema import RSIEMAStrategy
from strategies.breakout import BreakoutStrategy
from strategies.momentum import MomentumStrategy
from strategies.reversal import ReversalStrategy
from strategies.range_trading import RangeTradingStrategy
from strategies.volatility import VolatilityStrategy


def fetch_ohlcv(symbol, timeframe='1h', limit=1000):
    import ccxt
    exchange = ccxt.binance()
    exchange.load_markets()  # <-- das ist die magische Zeile!
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


def get_market_state(engine, ohlcv):
    # Nutze die Engine wie im Paper Loop für Marktklassifizierung
    ohlcv_list = ohlcv[['timestamp','open','high','low','close','volume']].values.tolist()
    return engine.evaluate_market(ohlcv_list)

def run_backtest(symbol, ohlcv, out_csv="backtest_results.csv", initial_balance=20.0):
    strategies = [
        RSIEMAStrategy(),
        BreakoutStrategy(),
        MomentumStrategy(),
        ReversalStrategy(),
        RangeTradingStrategy(),
        VolatilityStrategy()
    ]
    engine = StrategyEngine()
    balance = initial_balance
    trades = []
    position = None

    for i in range(50, len(ohlcv)):  # 50, damit Indikatoren stabil sind
        window = ohlcv.iloc[i-50:i]
        price = window['close'].iloc[-1]
        atr = window['high'].max() - window['low'].min()  # grober ATR Ersatz
        market_state = get_market_state(engine, window)
        # Wähle die Strategie mit Engine
        strat = engine.select_strategy(window[['timestamp','open','high','low','close','volume']].values.tolist())
        # Signal bestimmen
        try:
            signal = strat.generate_signal(window[['timestamp','open','high','low','close','volume']].values.tolist())
            print(f"{i=} {strat.__class__.__name__} signal={signal}")

        except Exception as e:
            print(f"Fehler in Signal-Generierung bei {strat.__class__.__name__}: {e}")
            continue

        # Wenn kein Signal, nächsten Durchlauf
        if not signal:
            continue

        # StopLoss/TakeProfit flexibel abrufen (mit Fallback für alte Signatur)
        side = signal
        volatility = atr / price if price > 0 else 0
        try:
            sl, tp = strat.sl_tp(price, atr, side, market_state, volatility)
        except TypeError:
            try:
                sl, tp = strat.sl_tp(price, atr, side)
            except TypeError:
                sl, tp = strat.sl_tp(price, atr)

        qty = 1  # Für Backtest einfach mit 1 Einheit traden, du kannst hier dynamisch machen!
        entry_price = price
        exit_price = None
        pnl = None

        # Simpler TP/SL Ausstieg im nächsten Candle
        future_window = ohlcv.iloc[i+1:i+10] if (i+10) < len(ohlcv) else ohlcv.iloc[i+1:]
        for idx, futrow in future_window.iterrows():
            high = futrow['high']
            low = futrow['low']
            if side == "BUY":
                if high >= tp:
                    exit_price = tp
                    break
                elif low <= sl:
                    exit_price = sl
                    break
            elif side == "SELL":
                if low <= tp:
                    exit_price = tp
                    break
                elif high >= sl:
                    exit_price = sl
                    break

        if exit_price is None:
            # Wenn weder TP noch SL erreicht, zum Schlusskurs aussteigen
            exit_price = future_window['close'].iloc[-1]

        if side == "BUY":
            pnl = (exit_price - entry_price) * qty
        elif side == "SELL":
            pnl = (entry_price - exit_price) * qty
        else:
            pnl = 0

        trade = {
            'timestamp': window['timestamp'].iloc[-1],
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'stop_loss': sl,
            'take_profit': tp,
            'qty': qty,
            'exit_price': exit_price,
            'pnl': pnl,
            'strategy': strat.__class__.__name__,
            'market_state': market_state
        }
        trades.append(trade)
        balance += pnl

    df_trades = pd.DataFrame(trades)
    df_trades.to_csv(out_csv, index=False)
    print(f"Backtest abgeschlossen. Ergebnisse in {out_csv} gespeichert.")

def main(symbol="BTCUSDT", timeframe="1h", candles=1000, out_csv="backtest_results.csv"):
    print(f"Lade OHLCV für {symbol}, Intervall {timeframe}, Anzahl {candles} ...")
    ohlcv = fetch_ohlcv(symbol, timeframe, limit=candles)
    run_backtest(symbol, ohlcv, out_csv=out_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="BTCUSDT")
    parser.add_argument("--timeframe", type=str, default="1h")
    parser.add_argument("--candles", type=int, default=1000)
    parser.add_argument("--out", type=str, default="backtest_results.csv")
    args = parser.parse_args()

    main(symbol=args.symbol, timeframe=args.timeframe, candles=args.candles, out_csv=args.out)
