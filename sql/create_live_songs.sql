CREATE TABLE live_songs (
    live_song_id BIGINT PRIMARY KEY,
    show_id BIGINT NOT NULL,
    song_id INT NOT NULL,
    set_number TEXT NOT NULL,
    position INT NOT NULL,
    transition TEXT,
    footnote TEXT,
    jamchart BOOLEAN NOT NULL,
    jamchart_notes TEXT,
    parent BOOLEAN NOT NULL,
    hof BOOLEAN NOT NULL,
    jimmy_stewart BOOLEAN NOT NULL,
    with_lyrics BOOLEAN NOT NULL
)