WITH shows_venues AS (
	SELECT show_id, show_date, shows.venue_id, venue_name, state, city
    FROM shows JOIN venues ON shows.venue_id=venues.venue_id
)

SELECT
	shows_venues.venue_id,
    MAX(venue_name) AS venue_name,
    MAX(state) AS state,
    MAX(city) AS city,
    COUNT(DISTINCT shows_venues.show_id) AS count,
    GROUP_CONCAT(DISTINCT show_date SEPARATOR ",") show_dates,
    -- TODO: Add marker for "noteworthy" shows
	SUM(jimmy_stewart) AS jimmy_stewart,
	SUM(with_lyrics) AS with_lyrics,
	SUM(hof) AS hof
FROM shows_venues LEFT JOIN live_songs ON shows_venues.show_id=live_songs.show_id
GROUP BY venue_id
ORDER BY venue_name
