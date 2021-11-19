WITH jimmy_stewarts AS (
	SELECT show_date, song_id, jimmy_stewart, with_lyrics, hof
    FROM live_songs JOIN shows ON live_songs.show_id=shows.show_id
    WHERE parent='1' AND jimmy_stewart='1'
)

SELECT
	show_date, name, jimmy_stewart, with_lyrics, hof
FROM jimmy_stewarts JOIN songs ON jimmy_stewarts.song_id=songs.song_id
ORDER BY show_date
