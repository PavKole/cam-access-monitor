-- Таблица событий прохода по пропускам
CREATE TABLE IF NOT EXISTS events (
    id          SERIAL PRIMARY KEY,
    card_id     VARCHAR(64)  NOT NULL,        -- номер карты
    user_name   VARCHAR(128),                 -- имя владельца (может быть пустым)
    direction   VARCHAR(8)   NOT NULL,        -- 'in' или 'out'
    gate        VARCHAR(64),                  -- какой турникет/дверь
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Индекс по времени — чтобы быстро получать "последние N событий"
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at DESC);

-- Индекс по карте — чтобы быстро искать историю по конкретному пропуску
CREATE INDEX IF NOT EXISTS idx_events_card_id ON events (card_id);
