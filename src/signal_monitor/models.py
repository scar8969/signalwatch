from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Signal(db.Model):
    __tablename__ = "signals"
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(64), default="")
    side = db.Column(db.String(8), default="")  # BUY|SELL
    price = db.Column(db.Float, default=0.0)
    size = db.Column(db.Integer, default=1)
    ts = db.Column(db.DateTime, default=datetime.utcnow)


class Trade(db.Model):
    __tablename__ = "trades"
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.Integer, db.ForeignKey("signals.id"))
    entry = db.Column(db.Float, default=0.0)
    exit = db.Column(db.Float, nullable=True)
    pnl = db.Column(db.Float, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)


class Equity(db.Model):
    __tablename__ = "equity"
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    value = db.Column(db.Float, default=0.0)
