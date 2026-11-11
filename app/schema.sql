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


-- ===== Subsystem 2 (Energy Monitoring): readings belong to a device of Subsystem 1 =====
CREATE TABLE IF NOT EXISTS energy_reading (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id    INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    date         TEXT NOT NULL,              -- YYYY-MM-DD
    amount_kwh   REAL NOT NULL CHECK (amount_kwh > 0),
    is_simulated INTEGER NOT NULL DEFAULT 0 CHECK (is_simulated IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_reading_date   ON energy_reading(date);
CREATE INDEX IF NOT EXISTS idx_reading_device ON energy_reading(device_id);

-- ===== Subsystem 3 (Cost, Carbon, Goals, Alerts): belong to a building of Subsystem 1 =====
CREATE TABLE IF NOT EXISTS energy_settings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id        INTEGER NOT NULL REFERENCES users(id),
    building_id     INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    price_per_kwh   REAL NOT NULL CHECK (price_per_kwh >= 0),
    emission_factor REAL NOT NULL CHECK (emission_factor >= 0),
    factor_source   TEXT NOT NULL,
    UNIQUE (owner_id, building_id)
);
CREATE TABLE IF NOT EXISTS energy_goals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id        INTEGER NOT NULL REFERENCES users(id),
    building_id     INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    target_kwh      REAL NOT NULL CHECK (target_kwh > 0),
    month           TEXT NOT NULL,           -- YYYY-MM
    daily_limit_kwh REAL NOT NULL CHECK (daily_limit_kwh > 0),
    UNIQUE (owner_id, building_id, month)
);
CREATE TABLE IF NOT EXISTS energy_alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id    INTEGER NOT NULL REFERENCES users(id),
    building_id INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    message     TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    is_read     INTEGER NOT NULL DEFAULT 0
);

-- ===== Subsystem 4 (AI Coach and Reports) =====
CREATE TABLE IF NOT EXISTS reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    building_id  INTEGER NOT NULL REFERENCES buildings(id) ON DELETE CASCADE,
    period       TEXT NOT NULL,              -- YYYY-MM
    created_date TEXT NOT NULL
);
