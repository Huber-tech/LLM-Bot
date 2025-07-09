# utils/grid_manager.py

from utils.equity import get_equity_scaling_factor

class GridManager:
    def __init__(self, grid_distance_pct=0.005, levels=3):
        self.grid_distance_pct = grid_distance_pct
        self.levels = levels

    def generate_grid_orders(self, entry_price, side):
        grid_prices = []
        for i in range(1, self.levels + 1):
            pct = self.grid_distance_pct * i
            if side == "BUY":
                grid_price = entry_price * (1 - pct)
            else:
                grid_price = entry_price * (1 + pct)
            grid_prices.append(grid_price)
        return grid_prices

    def scale_order_qty(self, base_qty):
        factor = get_equity_scaling_factor()
        return round(base_qty * factor, 4)
