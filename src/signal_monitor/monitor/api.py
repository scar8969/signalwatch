from flask import Blueprint, jsonify, request

from ..models import Signal, Trade
from .alerts import alert
from .pnl import drawdown, equity_curve, stats
from .signals import ingest, validate

bp = Blueprint("monitor", __name__)


@bp.post("/api/signals")
def add_signal():
    d = request.get_json(force=True, silent=True) or {}
    try:
        validate(d.get("side", ""), d.get("price", 0), d.get("size", 1))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    sig = ingest(d.get("strategy", "SMA-cross"), d["side"], d["price"], d.get("size", 1))
    alert(sig)
    return jsonify({"id": sig.id, "status": "open"})


@bp.get("/api/signals")
def list_signals():
    return jsonify(
        {
            "signals": [
                {
                    "id": s.id,
                    "strategy": s.strategy,
                    "side": s.side,
                    "price": s.price,
                    "ts": s.ts.isoformat() if s.ts else "",
                }
                for s in Signal.query.order_by(Signal.id.desc()).limit(50).all()
            ]
        }
    )


@bp.get("/api/equity")
def equity():
    trades = Trade.query.all()
    curve = equity_curve(trades)
    max_dd, cur_dd = drawdown(curve)
    return jsonify({"series": curve, "max_dd": max_dd, "current_dd": cur_dd})


@bp.get("/api/stats")
def get_stats():
    return jsonify(stats(Trade.query.all()))


@bp.post("/api/replay/start")
def start_replay():
    d = request.get_json(force=True, silent=True) or {}
    return jsonify({"replay_id": 1, "speed": d.get("speed", 1.0)})
