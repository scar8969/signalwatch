"""Flask application for signal-monitor.

Assembled from the project skeleton by _tools/build.py.  The wiring the skeleton
cannot express lives here: an absolute template folder, an instance folder that
exists before SQLAlchemy resolves the relative sqlite path, and the HTML pages
(live blotter, replay, ledger) that read the real signals/trades/equity tables.

Two deliberate properties of every GET path here:

* nothing blocks.  monitor.alerts.alert() posts to Telegram inside a try/except
  with a 10 s timeout and is only reachable from POST /api/signals, never from a
  page render.
* /api/signals/stream is a *bounded* SSE burst (frames query param, default 3,
  then an "event: end" frame).  Browser EventSource reconnects automatically, so
  a bounded response is the normal way to serve SSE without pinning a worker for
  the lifetime of the client.
"""
import json
import time

from .models import Equity, Signal, Trade, db
from .monitor.alerts import alert
from .monitor.api import bp
from .monitor.pnl import drawdown, equity_curve, stats
from . import paths

from flask import (Flask, Response, flash, jsonify, redirect, render_template, request, url_for)

paths.ensure_runtime_dirs()

def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR),
                instance_path=str(paths.INSTANCE_DIR))
    app.secret_key = "signalmonitor-dev"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(paths.INSTANCE_DIR / "signalmonitor.db")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    SIDE_OK = ("BUY", "SELL")

    def _bars(points, width=32):
        """Normalise an equity curve into 0-100 bar heights for the CSS chart."""
        if not points:
            return []
        values = [p["value"] for p in points if p["value"] is not None] or [0.0]
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1.0
        step = max(1, len(points) // width)
        out = []
        for p in points[::step]:
            pct = 100.0 if hi == lo else (p["value"] - lo) / span * 100.0
            out.append({"t": p["when"], "value": p["value"], "pct": round(max(2.0, pct), 1)})
        return out

    @app.get("/")
    def index():
        signals = Signal.query.order_by(Signal.id.desc()).limit(50).all()
        trades = Trade.query.all()
        curve = equity_curve(trades)
        max_dd, cur_dd = drawdown(curve)
        summary = stats(trades)
        points = [{"when": c[0], "value": c[1]} for c in curve]
        return render_template("index.html", signals=signals, trades=trades,
                               summary=summary, max_dd=max_dd, cur_dd=cur_dd,
                               bars=_bars(points), curve_points=len(points))

    @app.post("/signals")
    def signal_create():
        """HTML equivalent of POST /api/signals (which needs a JSON body).

        Validated with the same rules as monitor.signals.validate so the page and the
        API reject the same inputs with the same messages.  monitor.alerts.alert() is
        called too; it swallows its own network errors by design.
        """
        side = (request.form.get("side") or "").strip().upper()
        strategy = (request.form.get("strategy") or "SMA-cross").strip()
        try:
            price = float(request.form.get("price") or 0)
        except ValueError:
            price = 0.0
        try:
            size = float(request.form.get("size") or 1)
        except ValueError:
            size = 0.0
        if side not in SIDE_OK:
            flash("side must be BUY or SELL", "no")
            return redirect(url_for("index"))
        if price <= 0 or size <= 0:
            flash("price and size must be positive", "no")
            return redirect(url_for("index"))
        sig = Signal(strategy=strategy, side=side, price=price, size=size)
        db.session.add(sig)
        db.session.commit()
        try:
            alert(sig)
        except Exception:
            pass
        flash("recorded %s %s @ %s" % (side, strategy, price))
        return redirect(url_for("index"))

    @app.get("/replay")
    def replay_view():
        signals = Signal.query.order_by(Signal.id).all()
        trades = Trade.query.filter(Trade.closed_at.isnot(None)).order_by(Trade.closed_at).all()
        curve = equity_curve(trades)
        return render_template("replay.html", signals=signals, trades=trades,
                               curve_points=len(curve),
                               bars=_bars([{"when": c[0], "value": c[1]} for c in curve]))

    @app.get("/ledger")
    def ledger():
        trades = Trade.query.order_by(Trade.id.desc()).all()
        summary = stats(trades)
        curve = equity_curve(trades)
        max_dd, cur_dd = drawdown(curve)
        equity_rows = Equity.query.order_by(Equity.ts.desc()).limit(50).all()
        return render_template("ledger.html", trades=trades, summary=summary,
                               max_dd=max_dd, cur_dd=cur_dd, equity_rows=equity_rows)

    @app.get("/api/signals/stream")
    def signals_stream():
        """Bounded server-sent events feed consumed by replay.html.

        frames=N    how many frames to emit (default 3, clamped to 1..600)
        interval=S  seconds between frames (default 1.0, clamped to 0.1..60)
        A final "event: end" frame closes the response; EventSource reconnects.
        """
        try:
            frames = max(1, min(600, int(request.args.get("frames", 3))))
        except (TypeError, ValueError):
            frames = 3
        try:
            interval = min(60.0, max(0.1, float(request.args.get("interval", 1.0))))
        except (TypeError, ValueError):
            interval = 1.0

        def gen():
            last = 0
            sent = 0
            while sent < frames:
                with app.app_context():
                    fresh = Signal.query.filter(Signal.id > last).order_by(Signal.id).all()
                    for s in fresh:
                        last = max(last, s.id)
                        yield "data: " + json.dumps({"id": s.id, "side": s.side,
                                                     "strategy": s.strategy,
                                                     "price": s.price}) + "\n\n"
                sent += 1
                if sent < frames:
                    time.sleep(interval)
            yield "event: end\ndata: {}\n\n"

        return Response(gen(), mimetype="text/event-stream")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "signals": Signal.query.count(),
                        "trades": Trade.query.count()})

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=8000)

    return app

app = build_app()
