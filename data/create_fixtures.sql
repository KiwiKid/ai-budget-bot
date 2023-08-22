CREATE TABLE IF NOT EXISTS transactions (
    t_id TEXT NOT NULL,
    ts_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount TEXT NOT NULL,
    status TEXT NOT NULL,
    category TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS headers (
    ts_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    amount_head TEXT NOT NULL,
    date_head TEXT NOT NULL,
    description_head TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
