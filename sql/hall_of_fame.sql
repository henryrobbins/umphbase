WITH hofs AS (
	SELECT show_date, song_id, jimmy_stewart, with_lyrics, hof
    FROM live_songs JOIN shows ON live_songs.show_id=shows.show_id
    WHERE parent='1' AND hof='1'
)

SELECT
	show_date, songs.song_id, name, jimmy_stewart, with_lyrics, hof
FROM hofs JOIN songs ON hofs.song_id=songs.song_id
ORDER BY show_date
