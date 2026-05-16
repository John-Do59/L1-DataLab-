-- Schéma minimal pour l'API Applicative
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prediction_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    match_id VARCHAR(50),
    predicted_result VARCHAR(1),
    actual_result VARCHAR(1),
    prediction_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
