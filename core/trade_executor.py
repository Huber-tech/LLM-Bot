from utils.logger import logger
from strategies.indicators import calculate_atr
from binance.enums import *

SIDE_Buy = "Buy"

class TradeExecutor:
    def __init__(self, client, base_currency: str = "USDC"):
        self.client = client
        self.base_currency = base_currency

    async def execute_trade(
        self,
        symbol: str,
        side: str,
        quantity: float,
        sl: float = None,
        tp: float = None,
        atr_period: int = 14,
        sl_multiplier: float = 1.5,
        tp_multiplier: float = 3.0,
        martingale_factor: float = 1.0,
        paper: bool = True
    ):
        qty = quantity * martingale_factor
        logger.info(f"Placing {side} order for {symbol} qty={qty:.6f} (martingale={martingale_factor})")

        # Preis ermitteln
        if paper:
            price = await self.client.get_futures_price(symbol)
            logger.info(f"(Paper) Order simulated at {price}")
        else:
            order = await self.client.client.futures_create_order(
                symbol=symbol,
                side=side,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=qty
            )
            price = float(order["avgPrice"])
            logger.info(f"Order executed at price={price}")

        # SL/TP berechnen wenn nicht manuell übergeben
        if sl is None or tp is None:
            ohlcv = await self.client.fetch_ohlcv(symbol, timeframe='1h', limit=atr_period + 1)
            atr = calculate_atr(ohlcv, period=atr_period)
            sl, tp = self._compute_sl_tp(price, atr, side, sl_multiplier, tp_multiplier)

        return {
            "entry_price": price,
            "sl_price": sl,
            "tp_price": tp,
            "qty": qty
        }

    def _compute_sl_tp(self, entry: float, atr: float, side: str,
                       sl_mult: float, tp_mult: float):
        if side == SIDE_BUY:
            sl = entry - atr * sl_mult
            tp = entry + atr * tp_mult
        else:
            sl = entry + atr * sl_mult
            tp = entry - atr * tp_mult
        return sl, tp
