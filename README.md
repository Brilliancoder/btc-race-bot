# cbBTC EMA trend bot

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/Brilliancoder/btc-race-bot/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/Brilliancoder/btc-race-bot/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Entry for the make.fun bounty **btc-race-24h-20261123-0511**: trades cbBTC/USDC on 1-minute bars
(agent-fun/bars-replay/v1), long only, from 1,000 USDC paper money.

Strategy: EMA trend following with an RSI filter and a trailing stop.
- Buy with all cash when EMA(30) > EMA(120) and Wilder RSI(14) < 75.
- Sell the whole position when EMA(30) < EMA(120) or the close falls 1.5% below its peak since entry,
  after holding at least 30 bars.

Run: `python3 -P -s main.py` (standard library only; `vendor/makefun_bars.py` is the kit's SDK shim, unmodified).
`sweep.py <bars.ndjson.gz>` is an approximate offline parameter sweep over the dev bars.

Local dev grade: net PnL +7.42 USDC, max drawdown 3.2%, 11 trades.

License: MIT.
