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


CREATE TABLE IF NOT EXISTS outbox_events (
    id UUID PRIMARY KEY,

    aggregate_type TEXT NOT NULL,   -- например: 'order'
    aggregate_id   TEXT NOT NULL,   -- order_id (o_xxx)

    event_type TEXT NOT NULL,       -- 'order.confirmed'
    payload JSONB NOT NULL,         -- данные события

    created_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP          -- NULL = ещё не отправлено
);

CREATE INDEX IF NOT EXISTS idx_outbox_unprocessed
    ON outbox_events (processed_at)
    WHERE processed_at IS NULL;
