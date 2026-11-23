"""Approximate offline sweep of main.Strategy on the dev bars (fills at next open, 4 bps fee + 2 bps slip + impact)."""

import gzip
import itertools
import json
import sys

import main

bars = [json.loads(l) for l in gzip.open(sys.argv[1])]


def sim(p):
    s = main.Strategy(**p)
    cash, qty, trades, peak, dd = 1000.0, 0.0, 0, 1000.0, 0.0
    pending = None
    for b in bars:
        o, c, depth = int(b["o"]) / 1e5, int(b["c"]) / 1e5, int(b["o_depth"][0]) / 1e6
        if pending == "buy":
            net = cash * (1 - 4e-4)
            qty, cash, trades = net / (o * 1.0002 * (1 + net / depth)), 0.0, trades + 1
        elif pending == "sell":
            v = qty * o
            cash, qty, trades = v / (1.0002 * (1 + v / depth)) * (1 - 4e-4), 0.0, trades + 1
        s.held = qty > 0
        pending = s.step(int(b["c"]))
        eq = cash + qty * c
        peak = max(peak, eq)
        dd = max(dd, 1 - eq / peak)
    if qty:
        cash += qty * c * (1 - 1e-3)
    return cash - 1000, dd, trades


grid = {"fast": [10, 20, 30, 60], "slow": [60, 120, 240], "rsi_n": [14], "rsi_max": [70, 80, 101],
        "trail": [0.004, 0.008, 0.012, 0.02], "min_hold": [0, 30]}
res = []
for vals in itertools.product(*grid.values()):
    p = dict(zip(grid, vals))
    if p["fast"] >= p["slow"]:
        continue
    res.append((sim(p), p))
res.sort(key=lambda r: -r[0][0])
for r in res[:25]:
    print("pnl %.2f dd %.3f trades %d" % r[0], r[1])
print("current", sim(main.PARAMS))
