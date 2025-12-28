# user_service/schema.sql

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,

    telegram_id BIGINT UNIQUE NOT NULL,

    username TEXT,
    first_name TEXT,
    last_name TEXT,

    commission NUMERIC(5,4) NOT NULL DEFAULT 0.0100,
    total_volume NUMERIC(20,8) NOT NULL DEFAULT 0,

    payment_info JSONB,

    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id
    ON users (telegram_id);
