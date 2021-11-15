import os
import sys
import pandas as pd
import numpy as np


def clean_songs(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a songs dataframe pulled from ATU."""
    df = (df.reset_index()
            .rename(columns={'@id': 'song_id',
                             'isoriginal': 'original'}))
    assert len(df['slug'].unique()) == len(df)
    df = df.set_index('slug')
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.where((pd.notnull(df)), None)

    # fix E.T.I. Blue Öyster Cult typo from database
    df.at['eti', 'original_artist'] = 'Blue Öyster Cult'

    df = df.reset_index()
    df = df[['song_id', 'name', 'slug',
             'original_artist', 'original']]
    assert sum(df['name'].isna()) == 0

    return df


def clean_venues(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a venues dataframe pulled from ATU."""
    df = df.drop_duplicates()
    df = df.rename(columns={'slug': 'venue_id',
                            'venuename': 'venue_name'})
    assert len(df['venue_id'].unique()) == len(df)
    df = df.set_index('venue_id')
    df = df[['venue_name', 'city', 'state', 'country']]
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.where((pd.notnull(df)), None)

    # errors in the database
    df = df.drop('camp-buzz')
    df.at['velvet-lounge-washington-dc', 'state'] = 'DC'
    df.at['velvet-lounge-washington-dc', 'country'] = 'USA'

    df = df.reset_index()

    return df


def clean_shows(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a shows dataframe pulled from ATU."""
    assert len(df['show_id'].unique()) == len(df)
    df = df.drop(columns='venue_id')
    df = df.rename(columns={'venuename': 'venue_name',
                            'showdate': 'show_date',
                            'tourname': 'tour_name',
                            'showorder': 'show_order'})
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.where((pd.notnull(df)), None)
    return df


def clean_live_songs(df: pd.DataFrame) -> pd.DataFrame:
    """Clean a live songs dataframe pulled from ATU."""
    df = df.rename(columns={'uniqueid': 'live_song_id',
                            'setnumber': 'set_number',
                            'isjamchart': 'jamchart',
                            'soundcheck': 'sound_check',
                            'shownotes': 'show_notes'})
    # 1508604129 show_id entries are duplicates of 1508604143
    df = df[~(df.show_id == '1508604129')]
    assert len(df['live_song_id'].unique()) == len(df)
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.where((pd.notnull(df)), None)
    df['transition'] = (df['transition']
                        .replace(to_replace=' > ', value='>')
                        .replace(to_replace=', ', value=',')
                        .replace(to_replace='  ', value=np.nan))
    df['show_notes'] = df['show_notes'].str.strip('\r\n')

    # assign a parent (first occurrence) for song sandwiches
    df['parent'] = '1'
    children = df[['show_id', 'song_id']].duplicated(keep='first')
    df.loc[children, 'parent'] = '0'

    keep = ['live_song_id', 'show_id', 'song_id', 'parent', 'set_number',
            'position', 'transition', 'footnote', 'jamchart', 'jamchart_notes',
            'show_notes', 'opener', 'sound_check']
    df = df[keep]

    return df


def main(to_path: str, from_path: str):
    """Take an unclean ATU pull at a given path and clean it."""
    songs_df = clean_songs(pd.read_pickle('%s/songs.pickle' % from_path))
    venues_df = clean_venues(pd.read_pickle('%s/venues.pickle' % from_path))
    shows_df = clean_shows(pd.read_pickle('%s/shows.pickle' % from_path))
    live_songs_df = clean_live_songs(pd.read_pickle('%s/live_songs.pickle' % from_path))

    # Some songs in songs_df do not have live performaces
    # for one of the following reasons:
    #  - In the discography with no live performace
    #  - Appears as a tease/jam without its own entry in a set
    # For now, we drop these songs from the database
    no_live_performances = []
    for song_id in songs_df["song_id"]:
        if len(live_songs_df[live_songs_df.song_id == str(song_id)]) == 0:
            no_live_performances.append(song_id)
    songs_df = songs_df[~(songs_df.song_id.isin(no_live_performances))]

    # Merge in venues data to reduce data redundancy
    len_before_merge = len(shows_df)
    shows_df = shows_df.merge(venues_df,
                              on=['venue_name', 'city', 'state', 'country'],
                              how='inner')
    assert len_before_merge == len(shows_df)
    shows_df = shows_df[['show_id', 'show_date', 'artist', 'venue_id',
                        'tour_name', 'show_order']]

    # Keep some columns which contain missing show information
    extra_cols = (live_songs_df[['show_id', 'show_notes',
                                 'opener', 'sound_check']]
                  .drop_duplicates())
    keep = ['live_song_id', 'show_id', 'song_id', 'parent', 'set_number',
            'position', 'transition', 'footnote', 'jamchart', 'jamchart_notes']
    live_songs_df = live_songs_df[keep]

    # Add some missing columns to shows_df
    tmp = shows_df.merge(extra_cols, on='show_id', how='left')

    # Consolidate some column information for a few shows
    for i in tmp[tmp.show_id.duplicated('last')].index:
        for col in ['show_notes', 'opener', 'sound_check']:
            if tmp.at[i, col] is None:
                tmp.at[i, col] = tmp.at[i+1, col]
            if tmp.at[i+1, col] is None:
                tmp.at[i+1, col] = tmp.at[i, col]
    shows_df = tmp.drop_duplicates()
    shows_df = shows_df.where((pd.notnull(shows_df)), None)
    assert len(shows_df['show_id'].unique()) == len(shows_df)

    # Mark all hall of fame performances
    hof = pd.read_csv('data/hall_of_fame.csv', index_col=0)
    tmp = live_songs_df.merge(shows_df, on='show_id', how='left')
    tmp = tmp.merge(songs_df, on='song_id', how='left')
    hof_ids = (
        hof.merge(tmp, on=['show_date', 'name'], how='left')['live_song_id'])
    live_songs_df['hof'] = '0'
    live_songs_df.loc[live_songs_df['live_song_id'].isin(hof_ids), 'hof'] = '1'

    # Mark all Jimmy Stewart performances
    js = pd.read_csv('data/jimmy_stewarts.csv', index_col=0)
    tmp = live_songs_df.merge(shows_df, on='show_id', how='left')
    tmp = tmp.merge(songs_df, on='song_id', how='left')
    js_ids = (
        js.merge(tmp, on=['show_date', 'name'], how='left')['live_song_id'])
    live_songs_df['jimmy_stewart'] = '0'
    live_songs_df.loc[live_songs_df['live_song_id'].isin(js_ids), 'jimmy_stewart'] = '1'

    # Mark all Jimmy Stewart performances (with lyrics)
    js = pd.read_csv('data/jimmy_stewarts.csv', index_col=0)
    js = js[js['with_lyrics']]
    tmp = live_songs_df.merge(shows_df, on='show_id', how='left')
    tmp = tmp.merge(songs_df, on='song_id', how='left')
    js_ids = (
        js.merge(tmp, on=['show_date', 'name'], how='left')['live_song_id'])
    live_songs_df['with_lyrics'] = '0'
    live_songs_df.loc[live_songs_df['live_song_id'].isin(js_ids), 'with_lyrics'] = '1'

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
