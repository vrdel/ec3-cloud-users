CREATE TABLE users
(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    home INTEGER,
    pass INTEGER,
    passvalue TEXT,
    sge INTEGER,
    email INTEGER
);

CREATE INDEX idx_users_name ON users(username);
