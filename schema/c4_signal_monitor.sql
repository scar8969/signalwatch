-- 📈 signal-monitor schema
CREATE TABLE signals(id INTEGER PRIMARY KEY, strategy TEXT, side TEXT, price REAL, size INTEGER DEFAULT 1, ts DATETIME);
CREATE TABLE trades(id INTEGER PRIMARY KEY, signal_id INTEGER REFERENCES signals(id), entry REAL, exit REAL, pnl REAL, closed_at DATETIME);
CREATE TABLE equity(id INTEGER PRIMARY KEY, ts DATETIME, value REAL);
