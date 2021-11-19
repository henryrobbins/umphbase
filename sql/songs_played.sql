WITH shows_songs AS (
	SELECT
		song_id,
		show_date
	FROM live_songs JOIN shows ON live_songs.show_id=shows.show_id
)

SELECT
	songs.song_id,
	MAX(name) AS name,
    MAX(original_artist) AS original_artist,
    MIN(show_date) AS first_played,
    MAX(show_date) AS last_played
FROM songs JOIN shows_songs ON songs.song_id=shows_songs.song_id
GROUP BY song_id
ORDER BY name
