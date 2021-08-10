CREATE TABLE songs (
    song_id INT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL,
    original_artist TEXT,
    original BOOLEAN NOT NULL
)