-- The 3 tables of Subsystem 1 (User and Building Management)

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,      -- UNIQUE: the same email twice is not allowed
    password_hash TEXT NOT NULL,             -- never the real password
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS buildings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id),   -- the owner
    name         TEXT NOT NULL,
    address      TEXT NOT NULL,
    type         TEXT NOT NULL,              -- office / university / home
    comfort_temp REAL NOT NULL               -- degrees Celsius
);

CREATE TABLE IF NOT EXISTS devices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    building_id INTEGER NOT NULL REFERENCES buildings(id),
    name        TEXT NOT NULL,
    energy_type TEXT NOT NULL                -- electricity / gas / solar
);
