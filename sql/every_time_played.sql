SELECT
	live_songs.song_id AS song_id,
    live_songs.jimmy_stewart AS jimmy_stewart,
	live_songs.with_lyrics AS with_lyrics,
	live_songs.hof AS hof,
	shows.show_date AS show_date,
	live_songs.position AS position,
    live_songs.set_number AS set_number,
	song_before.song_id AS before_song_id,
	song_before.jimmy_stewart AS before_jimmy_stewart,
	song_before.with_lyrics AS before_with_lyrics,
	song_before.hof AS before_hof,
	song_before.transition AS before_transition,
	live_songs.transition AS after_transition,
	song_after.song_id AS after_song_id,
	song_after.jimmy_stewart AS after_jimmy_stewart,
	song_after.with_lyrics AS after_with_lyrics,
	song_after.hof AS after_hof
FROM live_songs LEFT JOIN live_songs AS song_before ON
	live_songs.show_id=song_before.show_id AND
	live_songs.position=(song_before.position + 1)
LEFT JOIN live_songs AS song_after ON
	live_songs.show_id=song_after.show_id AND
	live_songs.position=(song_after.position - 1)
JOIN shows ON live_songs.show_id=shows.show_id
ORDER BY song_id, show_date, position
