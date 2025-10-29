CREATE TABLE
    IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        metal TEXT NOT NULL,
        price REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (date, metal)
    );

CREATE INDEX IF NOT EXISTS idx_price_history_date_metal ON price_history (date, metal);