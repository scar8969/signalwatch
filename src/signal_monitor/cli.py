"""signal-monitor — command line over monitor/{api,pnl,signals,replay}.py."""
import argparse, asyncio, sys
from . import paths

def _db():
    """Open the SQLite session lazily (Flask-SQLAlchemy is not needed for --help)."""
    from flask import Flask
    from .models import db
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "signalmon.db")
    db.init_app(app)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    return db

def cmd_signal(args):
    from .monitor.signals import ingest, validate
    _db()
    try:
        validate(args.side.upper(), args.price, args.size)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    sig = ingest(args.strategy, args.side.upper(), args.price, args.size)
    print(f"signal #{sig.id} {sig.side} {sig.strategy} @ {sig.price}")
    return 0

def cmd_list(_args):
    from .models import Signal
    _db()
    rows = Signal.query.order_by(Signal.id.desc()).limit(50).all()
    if not rows:
        print("no signals")
        return 0
    for s in rows:
        ts = s.ts.isoformat() if s.ts else ""
        print(f"{s.id:<5} {ts:<26} {s.side:<5} {s.strategy:<12} @ {s.price}")
    return 0

def cmd_equity(_args):
    from .models import Trade
    from .monitor.pnl import drawdown, equity_curve
    _db()
    curve = equity_curve(Trade.query.all())
    max_dd, cur_dd = drawdown(curve)
    for _, v in curve:
        print(f"{v:>12.2f}")
    print(f"max_dd={max_dd}%  current_dd={cur_dd}%")
    return 0

def cmd_stats(_args):
    from .models import Trade
    from .monitor.pnl import stats
    _db()
    s = stats(Trade.query.all())
    for k, v in s.items():
        print(f"{k:<15} {v}")
    return 0

def cmd_replay(args):
    from .models import Signal
    from .monitor.replay import replay
    _db()
    signals = Signal.query.order_by(Signal.ts).all()

    async def go():
        count = 0
        async for s in replay(signals, args.speed):
            count += 1
            print(f"{s.side:<5} {s.strategy:<12} @ {s.price}")
        return count

    print(f"replaying {len(signals)} signals at {args.speed}x")
    print(f"done, {asyncio.run(go())} frames")
    return 0

def main():
    p = argparse.ArgumentParser(prog="signal-monitor")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("signal", help="record one signal")
    s.add_argument("side", choices=["BUY", "SELL", "buy", "sell"])
    s.add_argument("price", type=float)
    s.add_argument("--size", type=int, default=1)
    s.add_argument("--strategy", default="SMA-cross")
    sub.add_parser("list", help="list recent signals")
    sub.add_parser("equity", help="print the equity curve and drawdown")
    sub.add_parser("stats", help="print trade statistics")
    r = sub.add_parser("replay", help="replay stored signals in timestamp order")
    r.add_argument("--speed", type=float, default=1.0)
    args = p.parse_args()
    if args.cmd == "signal":
        return cmd_signal(args)
    if args.cmd == "list":
        return cmd_list(args)
    if args.cmd == "equity":
        return cmd_equity(args)
    if args.cmd == "stats":
        return cmd_stats(args)
    if args.cmd == "replay":
        return cmd_replay(args)
    p.print_help()
    return 1
