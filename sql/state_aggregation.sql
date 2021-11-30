WITH shows_venues AS (
	SELECT show_id, state, country
    FROM shows JOIN venues ON shows.venue_id=venues.venue_id
)

SELECT
	country,
	state,
    COUNT(DISTINCT shows_venues.show_id) AS count,
	SUM(jimmy_stewart) AS jimmy_stewart,
	SUM(with_lyrics) AS with_lyrics,
	SUM(hof) AS hof
FROM shows_venues LEFT JOIN live_songs ON shows_venues.show_id=live_songs.show_id
GROUP BY country, state
ORDER BY country, state
