import asyncio
from utils.backtester import Backtester

symbol_list = ["BTCUSDC", "ETHUSDC", "BNBUSDC", "SOLUSDC"]
start = "2025-01-01T00:00"
end = "2025-06-01T00:00"
granularity = "1h"
initial_balance = 20.0

async def run_backtests():
    tasks = []
    for symbol in symbol_list:
        bt = Backtester(
            symbol=symbol,
            start=start,
            end=end,
            granularity=granularity,
            initial_balance=initial_balance
        )
        tasks.append(bt.run())
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_backtests())
