WITH set_grouped AS (
	SELECT
		show_id,
		set_number,
		GROUP_CONCAT(songs.name ORDER BY position ASC SEPARATOR "<|>") AS name,
		GROUP_CONCAT(transition ORDER BY position ASC SEPARATOR "<|>") AS transition,
		GROUP_CONCAT(footnote ORDER BY position ASC SEPARATOR "<|>") AS footnote,
		GROUP_CONCAT(jimmy_stewart ORDER BY position ASC SEPARATOR ",") AS jimmy_stewart,
		GROUP_CONCAT(with_lyrics ORDER BY position ASC SEPARATOR ",") AS with_lyrics,
		GROUP_CONCAT(hof ORDER BY position ASC SEPARATOR ",") AS hof
	FROM live_songs JOIN songs ON live_songs.song_id=songs.song_id
	GROUP BY show_id, set_number
),

show_grouped AS (
	SELECT
		show_id,
		GROUP_CONCAT(set_number ORDER BY set_number ASC SEPARATOR ",") AS set_number,
		GROUP_CONCAT(name ORDER BY set_number ASC SEPARATOR "<sb>") AS name,
		GROUP_CONCAT(transition ORDER BY set_number ASC SEPARATOR "<sb>") AS transition,
		GROUP_CONCAT(footnote ORDER BY set_number ASC SEPARATOR "<sb>") AS footnote,
		GROUP_CONCAT(jimmy_stewart ORDER BY set_number ASC SEPARATOR "<sb>") AS jimmy_stewart,
		GROUP_CONCAT(with_lyrics ORDER BY set_number ASC SEPARATOR "<sb>") AS with_lyrics,
		GROUP_CONCAT(hof ORDER BY set_number ASC SEPARATOR "<sb>") AS hof
	FROM set_grouped
	GROUP BY show_id
),

shows_joined AS (
	SELECT
		show_date,
        venue_id,
        set_number,
        name,
        transition,
        footnote,
        jimmy_stewart,
        with_lyrics,
        hof,
        show_notes,
        opener
    FROM show_grouped JOIN shows ON show_grouped.show_id=shows.show_id
    ORDER BY show_date, show_order
)

SELECT
	show_date,
	venue_name,
    city,
    state,
    country,
	set_number,
	name,
	transition,
	footnote,
	jimmy_stewart,
	with_lyrics,
	hof,
	show_notes,
	opener
FROM shows_joined JOIN venues ON shows_joined.venue_id=venues.venue_id
ORDER BY show_date
