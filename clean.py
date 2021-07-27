import os
import sys
import pandas as pd
import numpy as np
import atu


def main(to_path: str, from_path: str):
    """
    Take an unclean ATU pull at a given path and clean it.
    """
    songs_df = pd.read_pickle('%s/songs.pickle' % from_path)
    venues_df = pd.read_pickle('%s/venues.pickle' % from_path)
    shows_df = pd.read_pickle('%s/shows.pickle' % from_path)
    live_songs_df = pd.read_pickle('%s/live_songs.pickle' % from_path)

    # SONGS Dataframe
    # ===============
    songs_df = (songs_df.reset_index()
                        .rename(columns={'@id': 'song_id',
                                         'isoriginal': 'original'}))
    assert len(songs_df['slug'].unique()) == len(songs_df)
    songs_df = songs_df.set_index('slug')
    songs_df = songs_df.replace(r'^\s*$', np.nan, regex=True)
    songs_df = songs_df.where((pd.notnull(songs_df)), None)

    # fix E.T.I. Blue Öyster Cult typo from database
    songs_df.at['eti', 'original_artist'] = 'Blue Öyster Cult'

    # songs_df read in with XML which can't read '&' properly
    # read these fields in with JSON to correct this
    for song in songs_df[songs_df.name.isna()].index:
        name = atu.request('songs/slug/%s' % song, 'json').at[0, 'name']
        songs_df.at[song, 'name'] = name
    for song in songs_df[songs_df.original_artist.isna()].index:
        original_artist = (atu.request('songs/slug/%s' % song, 'json')
                           .at[0, 'original_artist'])
        songs_df.at[song, 'original_artist'] = original_artist

    songs_df = songs_df.reset_index()
    songs_df = songs_df[['song_id', 'name', 'slug',
                         'original_artist', 'original']]
    assert sum(np.sum(songs_df.isna())) == 0

    # VENUES Dataframe
    # ================
    venues_df = venues_df.drop_duplicates()
    venues_df = venues_df.rename(columns={'slug': 'venue_id',
                                          'venuename': 'venue_name'})
    assert len(venues_df['venue_id'].unique()) == len(venues_df)
    venues_df = venues_df.set_index('venue_id')
    venues_df = venues_df[['venue_name', 'city', 'state', 'country']]
    venues_df = venues_df.replace(r'^\s*$', np.nan, regex=True)
    venues_df = venues_df.where((pd.notnull(venues_df)), None)

    # errors in the database
    venues_df = venues_df.drop('camp-buzz')
    venues_df.at['velvet-lounge-washington-dc', 'state'] = 'DC'
    venues_df.at['velvet-lounge-washington-dc', 'country'] = 'USA'

    venues_df = venues_df.reset_index()

    # SHOWS Dataframe
    # ===============
    assert len(shows_df['show_id'].unique()) == len(shows_df)
    shows_df = shows_df.drop(columns='venue_id')
    shows_df = shows_df.rename(columns={'venuename': 'venue_name',
                                        'showdate': 'show_date',
                                        'tourname': 'tour_name',
                                        'showorder': 'show_order'})
    shows_df = shows_df.replace(r'^\s*$', np.nan, regex=True)
    shows_df = shows_df.where((pd.notnull(shows_df)), None)
    len_before_merge = len(shows_df)
    shows_df = shows_df.merge(venues_df,
                              on=['venue_name', 'city', 'state', 'country'],
                              how='inner')
    assert len_before_merge == len(shows_df)
    shows_df = shows_df[['show_id', 'show_date', 'artist', 'venue_id',
                        'tour_name', 'show_order']]

    # LIVE_SONGS Dataframe
    # ====================
    live_songs_df = live_songs_df.rename(columns={'uniqueid': 'live_song_id',
                                                  'setnumber': 'set_number',
                                                  'isjamchart': 'jamchart',
                                                  'soundcheck': 'sound_check',
                                                  'shownotes': 'show_notes'})
    # 1508604129 show_id entries are duplicates of 1508604143
    live_songs_df = live_songs_df[~(live_songs_df.show_id == '1508604129')]
    assert len(live_songs_df['live_song_id'].unique()) == len(live_songs_df)
    live_songs_df = live_songs_df.replace(r'^\s*$', np.nan, regex=True)
    live_songs_df = live_songs_df.where((pd.notnull(live_songs_df)), None)
    live_songs_df['transition'] = (live_songs_df['transition']
                                   .replace(to_replace=' > ', value='>')
                                   .replace(to_replace=', ', value=',')
                                   .replace(to_replace='  ', value=np.nan))
    live_songs_df['show_notes'] = live_songs_df['show_notes'].str.strip('\r\n')
    extra_cols = (live_songs_df[['show_id', 'show_notes',
                                 'opener', 'sound_check']]
                  .drop_duplicates())
    keep = ['live_song_id', 'show_id', 'song_id', 'set_number', 'position',
            'transition', 'footnote', 'jamchart', 'jamchart_notes']
    live_songs_df = live_songs_df[keep]

    # Add some missing columns to shows_df
    tmp = shows_df.merge(extra_cols, on='show_id', how='left')

    # consolidate some column information for a few shows
    for i in tmp[tmp.show_id.duplicated('last')].index:
        for col in ['show_notes', 'opener', 'sound_check']:
            if tmp.at[i, col] is None:
                tmp.at[i, col] = tmp.at[i+1, col]
            if tmp.at[i+1, col] is None:
                tmp.at[i+1, col] = tmp.at[i, col]
    shows_df = tmp.drop_duplicates()
    shows_df = shows_df.where((pd.notnull(shows_df)), None)
    assert len(shows_df['show_id'].unique()) == len(shows_df)

    # Additional Processing
    # =====================

    # assign a parent (first occurence) for song sandwiches
    live_songs_df['parent'] = 1
    children = live_songs_df[['show_id', 'song_id']].duplicated(keep='first')
    live_songs_df.loc[children, 'parent'] = 0

    # mark all hall of fame performances
    hof = pd.read_csv('data/hall_of_fame.csv', index_col=0)
    tmp = live_songs_df.merge(shows_df, on='show_id', how='left')
    tmp = tmp.merge(songs_df, on='song_id', how='left')
    hof_ids = (
        hof.merge(tmp, on=['show_date', 'name'], how='left')['live_song_id'])
    live_songs_df['hof'] = 0
    live_songs_df.loc[live_songs_df['live_song_id'].isin(hof_ids), 'hof'] = 1

    # Write dataframes as pickle files
    # ================================

    if not os.path.exists(to_path):
        os.makedirs(to_path)
    songs_df.to_pickle('%s/songs.pickle' % to_path)
    venues_df.to_pickle('%s/venues.pickle' % to_path)
    shows_df.to_pickle('%s/shows.pickle' % to_path)
    live_songs_df.to_pickle('%s/live_songs.pickle' % to_path)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        main(sys.argv[1], sys.argv[2])
    else:
        main('atu_cleaned', 'atu_unclean')
