CREATE TABLE shows (
    show_id BIGINT PRIMARY KEY,
    show_date DATE NOT NULL,
    show_order TEXT NOT NULL,
    artist TEXT NOT NULL,
    venue_id TEXT NOT NULL,
    tour_name TEXT NOT NULL,
    show_notes LONGTEXT,
    opener TEXT,
    sound_check LONGTEXT
)