def validate(side, price, size):
    if side not in ("BUY", "SELL"):
        raise ValueError("side must be BUY or SELL")
    if price <= 0:
        raise ValueError("price must be positive")
    if size <= 0:
        raise ValueError("size must be positive")

def ingest(strategy, side, price, size):
    from ..models import Signal, db
    sig = Signal(strategy=strategy, side=side, price=price, size=size)
    db.session.add(sig)
    db.session.commit()
    return sig
