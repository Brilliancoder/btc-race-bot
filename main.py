"""cbBTC/USDC 1-minute bot: EMA fast/slow trend following with an RSI filter and a trailing stop."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

SYMBOL = "CBBTC"
PARAMS = {"fast": 30, "slow": 120, "rsi_n": 14, "rsi_max": 75, "trail": 0.015, "min_hold": 30}


class Strategy:
    """Pure signal logic: feed closes, get "buy", "sell" or None. Holds no account state beyond in/out."""

    def __init__(self, fast, slow, rsi_n, rsi_max, trail, min_hold):
        self.af, self.as_ = 2 / (fast + 1), 2 / (slow + 1)
        self.rsi_n, self.rsi_max, self.trail, self.min_hold = rsi_n, rsi_max, trail, min_hold
        self.warm = slow
        self.n = 0
        self.ef = self.es = self.prev = None
        self.gain = self.loss = 0.0
        self.held = False
        self.peak = 0.0
        self.age = 0

    def rsi(self):
        if self.loss == 0:
            return 100.0
        return 100 - 100 / (1 + self.gain / self.loss)

    def step(self, c):
        self.n += 1
        if self.prev is None:
            self.ef = self.es = c
        else:
            d = c - self.prev
            k = 1 / self.rsi_n
            self.gain += k * (max(d, 0) - self.gain)
            self.loss += k * (max(-d, 0) - self.loss)
            self.ef += self.af * (c - self.ef)
            self.es += self.as_ * (c - self.es)
        self.prev = c
        if self.n < self.warm:
            return None
        if not self.held:
            if self.ef > self.es and self.rsi() < self.rsi_max:
                self.held, self.peak, self.age = True, c, 0
                return "buy"
            return None
        self.age += 1
        self.peak = max(self.peak, c)
        if self.age >= self.min_hold and (self.ef < self.es or c < self.peak * (1 - self.trail)):
            self.held = False
            return "sell"
        return None


def main():
    strat = Strategy(**PARAMS)

    def on_batch(state, batch):
        bar = next((b for b in batch["bars"] if b["symbol"] == SYMBOL), None)
        if bar is None:
            return []
        held = state.positions.get(SYMBOL)
        strat.held = held is not None and held.qty > 0  # trust the account over our own guess (rejected fills)
        sig = strat.step(int(bar["c"]))
        if state.warming_up:
            return []
        if sig == "buy" and state.cash >= 2_000_000:
            return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": state.cash, "max_slippage_bps": 150}]
        if sig == "sell" and held is not None and held.qty > 0:
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty, "max_slippage_bps": 300}]
        return []

    makefun_bars.run(on_batch)


if __name__ == "__main__":
    main()
