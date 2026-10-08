def equity_curve(trades):
    curve, cum = [], 0.0
    def _key(t):
        # open trades (closed_at None) sort last; closed sort by closed_at
        return (t.closed_at is None, getattr(t.closed_at, "timestamp", lambda: 0)() if t.closed_at else 0, t.id)
    for t in sorted(trades, key=_key):
        if t.pnl is not None:
            cum += t.pnl
        curve.append([t.closed_at.isoformat() if t.closed_at else "", round(cum, 2)])
    return curve

def drawdown(equity):
    if not equity:
        return 0.0, 0.0
    peak = equity[0][1]
    max_dd, cur_dd = 0.0, 0.0
    for _, v in equity:
        peak = max(peak, v)
        dd = (peak - v) / peak * 100 if peak else 0
        max_dd = max(max_dd, dd)
        cur_dd = dd
    return round(max_dd, 2), round(cur_dd, 2)

def stats(trades):
    closed = [t for t in trades if t.pnl is not None]
    if not closed:
        return {"trades": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0}
    wins = [t.pnl for t in closed if t.pnl > 0]
    losses = [t.pnl for t in closed if t.pnl <= 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    return {"trades": len(closed),
            "win_rate": round(len(wins) / len(closed) * 100, 1),
            "avg_win": round(gross_win / len(wins), 2) if wins else 0,
            "avg_loss": round(gross_loss / len(losses), 2) if losses else 0,
            "profit_factor": round(gross_win / gross_loss, 2) if gross_loss else float("inf")}
