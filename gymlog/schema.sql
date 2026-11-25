CREATE TABLE IF NOT EXISTS workouts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,          -- YYYY-MM-DD
    exercise    TEXT    NOT NULL,          -- ör. Bench Press
    equipment   TEXT    NOT NULL,          -- ör. Barbell, Smith Machine
    sets        INTEGER NOT NULL CHECK (sets > 0),
    reps        INTEGER NOT NULL CHECK (reps > 0),
    weight_kg   REAL    NOT NULL CHECK (weight_kg >= 0),
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
