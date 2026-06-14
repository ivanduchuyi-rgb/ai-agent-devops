-- Trading Dashboard Schema for Supabase PostgreSQL
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS trades (
    id BIGSERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    type VARCHAR(10) NOT NULL,      -- BUY/SELL
    lot NUMERIC(10,2),
    open_price NUMERIC(15,5),
    close_price NUMERIC(15,5),
    profit NUMERIC(15,2),
    score INTEGER,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_trades_time ON trades(time DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_profit ON trades(profit) WHERE profit IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_trades_time_symbol ON trades(time DESC, symbol);

-- Optional: Enable Row Level Security (RLS) for future multi-user
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Enable read for all" ON trades FOR SELECT USING (true);
-- CREATE POLICY "Enable insert for authenticated" ON trades FOR INSERT WITH CHECK (true);