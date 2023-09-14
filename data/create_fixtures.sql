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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

ALTER TABLE transactions ADD COLUMN categorization_attempt int DEFAULT 0;

ALTER TABLE headers ADD COLUMN batch_name TEXT NULL;

-- Alter headers columns to be nullable
ALTER TABLE headers ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE headers ALTER COLUMN amount_head DROP NOT NULL;
ALTER TABLE headers ALTER COLUMN date_head DROP NOT NULL;
ALTER TABLE headers ALTER COLUMN description_head DROP NOT NULL;

ALTER TABLE headers 
ADD PRIMARY KEY (ts_id);

ALTER TABLE headers
ADD column is_published boolean DEFAULT false;