CREATE TABLE users
(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    home INTEGER,
    shared INTEGER,
    pass INTEGER,
    passvalue TEXT,
    sge INTEGER,
    maillist INTEGER,
    email INTEGER
);

CREATE INDEX idx_users_name ON users(username);
