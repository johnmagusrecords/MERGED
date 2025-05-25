class Settings:
    """Application settings"""
    
    def __init__(self):
        self.trade_interval = 300  # 5 minutes
        self.tp_move_percent = 0.5 / 100  # Move TP by 0.5% when price moves
        self.breakeven_trigger = 1 / 100  # Move SL to breakeven at 1% profit
        self.symbols = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "ADAUSD", "SOLUSD", "DOGEUSD", "DOTUSD", "MATICUSD", "BNBUSD"]
        self.lot_sizes = {
            "BTCUSD": 0.001, "ETHUSD": 0.01, "ADAUSD": 0.5, "XRPUSD": 100, "LTCUSD": 1,
            "SOLUSD": 10, "DOGEUSD": 1000, "DOTUSD": 10, "MATICUSD": 100, "BNBUSD": 1
        }
        self.default_lot_size = 0.01
