CREATE TABLE IF NOT EXISTS raffle_entries (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    shoe_size VARCHAR(10) NOT NULL,
    is_winner BOOLEAN NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT NOW()
);
