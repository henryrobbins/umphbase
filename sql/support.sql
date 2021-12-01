WITH ordered_shows AS (SELECT * FROM shows ORDER BY show_date)

-- TODO: be careful with the comma separator
SELECT
	opener,
    GROUP_CONCAT(show_date SEPARATOR ",") show_dates,
    GROUP_CONCAT(venue_name SEPARATOR ",") venue_names
FROM ordered_shows JOIN venues ON ordered_shows.venue_id=venues.venue_id
WHERE opener!='None'
GROUP BY opener
ORDER BY opener
