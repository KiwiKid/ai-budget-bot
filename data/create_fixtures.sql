CREATE EXTENSION pgcrypto;

CREATE TYPE transaction_status AS ENUM ('pending', 'complete');

CREATE TABLE IF NOT EXISTS transactions (
    t_id UUID NOT NULL,
    ts_id UUID NOT NULL,
    user_id UUID NOT NULL,
    date TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    amount decimal NOT NULL,
    status transaction_status NOT NULL,
    category TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS headers (
    ts_id UUID NOT NULL,
    user_id UUID NOT NULL,
    amount_head TEXT NOT NULL,
    date_head TEXT NOT NULL,
    description_head TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    custom_rules TEXT[] NULL,
    custom_categories TEXT[] NULL
);
