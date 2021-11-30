WITH shows_songs AS (
	SELECT
		song_id,
		YEAR(show_date) AS year
	FROM live_songs JOIN shows ON live_songs.show_id=shows.show_id
	WHERE parent='1'
)

SELECT
	shows_songs.song_id,
    MAX(name) AS name,
    year,
    COUNT(*) AS count
FROM shows_songs JOIN songs ON shows_songs.song_id=songs.song_id
GROUP BY song_id, year
ORDER BY name, year
