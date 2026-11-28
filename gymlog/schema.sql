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

-- Antrenman şablonları: ör. "Push günü" -> hareket listesi
CREATE TABLE IF NOT EXISTS templates (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    created_at  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS template_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id  INTEGER NOT NULL REFERENCES templates (id),
    position     INTEGER NOT NULL,
    exercise     TEXT    NOT NULL,
    equipment    TEXT    NOT NULL,
    sets         INTEGER CHECK (sets IS NULL OR sets > 0),        -- isteğe bağlı
    reps         INTEGER CHECK (reps IS NULL OR reps > 0),        -- isteğe bağlı
    weight_kg    REAL    CHECK (weight_kg IS NULL OR weight_kg >= 0)  -- isteğe bağlı
);
