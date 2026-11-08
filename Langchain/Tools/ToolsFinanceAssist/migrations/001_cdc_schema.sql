-- ============================================================================
-- CDC SCHEMA MIGRATION - Finance Database
-- Phase 1: Add PKs, standardize columns, add CDC columns to all tables
-- ============================================================================

-- -----------------------------------------------------------------------------
-- 1. ADD PRIMARY KEYS TO TABLES MISSING THEM
-- -----------------------------------------------------------------------------

-- physical: Add sr_no as AUTOINCREMENT PK
-- SQLite requires creating new table for AUTOINCREMENT PK
CREATE TABLE physical_new (
    sr_no INTEGER PRIMARY KEY AUTOINCREMENT,
    investment_name TEXT,
    field_of_invest TEXT,
    total_investment REAL,
    current_value REAL,
    investment_date TEXT
);

INSERT INTO physical_new (investment_name, field_of_invest, total_investment, current_value, investment_date)
SELECT investment_name, field_of_invest, total_investment, current_value, investment_date
FROM physical;

DROP TABLE physical;
ALTER TABLE physical_new RENAME TO physical;

-- stock: Add sr_no as AUTOINCREMENT PK
CREATE TABLE stock_new (
    sr_no INTEGER PRIMARY KEY AUTOINCREMENT,
    no_of_shares REAL,
    field_of_invest TEXT,
    invested_value REAL,
    current_value REAL,
    total_profit REAL,
    name TEXT,
    investment_date TEXT DEFAULT (date('now'))
);

INSERT INTO stock_new (no_of_shares, field_of_invest, invested_value, current_value, total_profit)
SELECT no_of_shares, field_of_invest, invested_value, current_value, total_profit
FROM stock;

DROP TABLE stock;
ALTER TABLE stock_new RENAME TO stock;

-- -----------------------------------------------------------------------------
-- 2. ADD MISSING COLUMNS
-- -----------------------------------------------------------------------------

-- saving: Add investment_date
ALTER TABLE saving ADD COLUMN investment_date TEXT DEFAULT (date('now'));

-- stock: name and investment_date already added in table recreation above

-- -----------------------------------------------------------------------------
-- 3. RENAME COLUMNS FOR CONSISTENCY
-- -----------------------------------------------------------------------------

-- mutual_fund: investment_name -> name
ALTER TABLE mutual_fund RENAME COLUMN investment_name TO name;

-- -----------------------------------------------------------------------------
-- 4. ADD CDC COLUMNS TO ALL TABLES
-- -----------------------------------------------------------------------------

-- mutual_fund (already has these from earlier, but ensure they exist)
ALTER TABLE mutual_fund ADD COLUMN status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED'));
ALTER TABLE mutual_fund ADD COLUMN superseded_by INTEGER REFERENCES mutual_fund(sr_no);
ALTER TABLE mutual_fund ADD COLUMN is_latest BOOLEAN DEFAULT 1;

-- fixed_deposit
ALTER TABLE fixed_deposit ADD COLUMN status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED'));
ALTER TABLE fixed_deposit ADD COLUMN superseded_by INTEGER REFERENCES fixed_deposit(sr_no);
ALTER TABLE fixed_deposit ADD COLUMN is_latest BOOLEAN DEFAULT 1;

-- physical
ALTER TABLE physical ADD COLUMN status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED'));
ALTER TABLE physical ADD COLUMN superseded_by INTEGER REFERENCES physical(sr_no);
ALTER TABLE physical ADD COLUMN is_latest BOOLEAN DEFAULT 1;

-- saving
ALTER TABLE saving ADD COLUMN status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED'));
ALTER TABLE saving ADD COLUMN superseded_by INTEGER REFERENCES saving(sr_no);
ALTER TABLE saving ADD COLUMN is_latest BOOLEAN DEFAULT 1;

-- stock
ALTER TABLE stock ADD COLUMN status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CLOSED'));
ALTER TABLE stock ADD COLUMN superseded_by INTEGER REFERENCES stock(sr_no);
ALTER TABLE stock ADD COLUMN is_latest BOOLEAN DEFAULT 1;

-- -----------------------------------------------------------------------------
-- 5. BACKFILL EXISTING DATA
-- -----------------------------------------------------------------------------

UPDATE mutual_fund SET status='ACTIVE', is_latest=1, superseded_by=NULL WHERE status IS NULL;
UPDATE fixed_deposit SET status='ACTIVE', is_latest=1, superseded_by=NULL WHERE status IS NULL;
UPDATE physical SET status='ACTIVE', is_latest=1, superseded_by=NULL WHERE status IS NULL;
UPDATE saving SET status='ACTIVE', is_latest=1, superseded_by=NULL WHERE status IS NULL;
UPDATE stock SET status='ACTIVE', is_latest=1, superseded_by=NULL WHERE status IS NULL;

-- -----------------------------------------------------------------------------
-- 6. VERIFICATION QUERIES
-- -----------------------------------------------------------------------------

-- Check all tables have CDC columns
SELECT 'mutual_fund' as table_name, sql FROM sqlite_master WHERE type='table' AND name='mutual_fund'
UNION ALL
SELECT 'fixed_deposit', sql FROM sqlite_master WHERE type='table' AND name='fixed_deposit'
UNION ALL
SELECT 'physical', sql FROM sqlite_master WHERE type='table' AND name='physical'
UNION ALL
SELECT 'saving', sql FROM sqlite_master WHERE type='table' AND name='saving'
UNION ALL
SELECT 'stock', sql FROM sqlite_master WHERE type='table' AND name='stock';

-- Check data
SELECT 'mutual_fund' as table, COUNT(*) as rows, SUM(CASE WHEN is_latest=1 THEN 1 ELSE 0 END) as latest FROM mutual_fund
UNION ALL
SELECT 'fixed_deposit', COUNT(*), SUM(CASE WHEN is_latest=1 THEN 1 ELSE 0 END) FROM fixed_deposit
UNION ALL
SELECT 'physical', COUNT(*), SUM(CASE WHEN is_latest=1 THEN 1 ELSE 0 END) FROM physical
UNION ALL
SELECT 'saving', COUNT(*), SUM(CASE WHEN is_latest=1 THEN 1 ELSE 0 END) FROM saving
UNION ALL
SELECT 'stock', COUNT(*), SUM(CASE WHEN is_latest=1 THEN 1 ELSE 0 END) FROM stock;