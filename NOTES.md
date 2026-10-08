== curl ==
# POST /api/signals  {"strategy":"SMA-cross","side":"BUY","price":24810,"size":1}
# GET  /api/signals
# GET  /api/equity
# GET  /api/stats
# POST /api/replay/start  {"speed":2}

== session plan ==
# Session 1: signals (validate/ingest) → tests
# Session 2: pnl (equity/drawdown/stats) → tests
# Session 3: api + web (equity chart) + replay → screenshots
# Session 4: alerts + ledger → README → CI/Docker/Pages → tag
