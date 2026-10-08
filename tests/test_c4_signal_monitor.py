"""C4 signal-monitor — tests. Run: pytest test_c4_signal_monitor.py"""
import sys, os

import pytest
from datetime import datetime

class FakeTrade:
    def __init__(self, pnl, closed=True):
        self.pnl = pnl
        self.closed_at = datetime.utcnow() if closed else None
        self.id = 0

def test_validate():
    from signal_monitor.monitor.signals import validate
    validate("BUY", 100, 1)
    with pytest.raises(ValueError):
        validate("HOLD", 100, 1)
    with pytest.raises(ValueError):
        validate("BUY", -5, 1)
    with pytest.raises(ValueError):
        validate("BUY", 100, 0)

def test_equity_curve():
    from signal_monitor.monitor.pnl import equity_curve
    curve = equity_curve([FakeTrade(10), FakeTrade(-5), FakeTrade(20)])
    assert curve[-1][1] == 25

def test_drawdown():
    from signal_monitor.monitor.pnl import drawdown
    equity = [[0, 100], [1, 120], [2, 90], [3, 110]]
    max_dd, cur_dd = drawdown(equity)
    assert max_dd == 25.0  # 120 → 90
    assert cur_dd == pytest.approx(8.33, abs=0.1)  # 120 → 110

def test_stats():
    from signal_monitor.monitor.pnl import stats
    s = stats([FakeTrade(10), FakeTrade(-5), FakeTrade(20)])
    assert s["trades"] == 3
    assert s["win_rate"] == pytest.approx(66.7, abs=0.1)
    assert s["profit_factor"] == 6.0  # 30/5

def test_stats_empty():
    from signal_monitor.monitor.pnl import stats
    assert stats([])["trades"] == 0
