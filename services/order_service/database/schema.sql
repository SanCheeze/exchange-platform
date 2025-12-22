CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    order_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,

    quote_id TEXT NOT NULL,
    pair TEXT NOT NULL,
    amount_in NUMERIC NOT NULL,
    amount_out NUMERIC NOT NULL,
    rate NUMERIC NOT NULL,
    commission NUMERIC NOT NULL,

    session_id TEXT,
    client_id TEXT,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
