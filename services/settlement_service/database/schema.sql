CREATE TABLE IF NOT EXISTS processed_events (
    event_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    kafka_partition INT NOT NULL,
    kafka_offset BIGINT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settlements (
    id UUID PRIMARY KEY,
    order_id TEXT NOT NULL,
    pair TEXT NOT NULL,
    amount_in NUMERIC(18,2) NOT NULL,
    amount_out NUMERIC(18,2) NOT NULL,
    rate NUMERIC(18,6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
