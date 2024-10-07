-- init.sql
CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    username TEXT,
    phone VARCHAR,
    tickets_count INTEGER,
    purchase_date TIMESTAMP
);