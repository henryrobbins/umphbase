import json
import sys
import os
import xmltodict
import pandas as pd
import numpy as np
import requests


# TODO: Determine issue with direction parameter
def get_df(request: str,
           form: str,
           order_by: str = "",
           # direction : str = "",
           limit: int = "0") -> pd.DataFrame:
    '''Return the response from a request to the ATU database.

    The ATU (All Things Umphrey's) database contains the history of
    setlists from Umphrey's McGee. This function takes a valid
    request to the API (v1). The form of valid requests can be found at
    https://allthings.umphreys.com/api/docs.

    Attributes:
        request (str): A valid request to the API (v1)
        form (str): {'json', 'xml'}.
        order_by (str): Column to order by. Defaults to None
        direction (str): {'asc', 'desc'}. Defaults to 'asc'
        limit (int): Maximum number of results to return

    Returns:
        pd.DataFrame: The pandas dataframe representing the response
    '''
    # &direction=%s" % (direction)
    query = "order_by=%s&limit=%s" % (order_by, str(limit))
    base = "https://allthings.umphreys.com/api/v1/"
    url = base + "%s.%s?%s" % (request, form, query)
    txt = requests.get(url).text
    print('Request: ' + "%s.%s?%s" % (request, form, query))
    if form == 'json':
        df_dict = json.loads(txt)['data']
    elif form == 'xml':
        df_dict = json.loads(json.dumps(xmltodict.parse(txt)))
        df_dict = df_dict['results']['result']
    return pd.DataFrame(df_dict)


# Create pandas dataframes
# ========================

shows_df = get_df('shows', 'json')
venues_df = get_df('venues', 'json')
jamcharts_df = get_df('jamcharts', 'json')
songs_df = get_df('songs', 'xml').set_index('@id')

# Some songs in songs_df do not have live performaces
# for one of the following reasons:
#  - In the discography with no live performace
#  - Appears as a tease/jam without its own entry in a set
# This list keeps track of songs that fall in this category
no_live_performs = []

setlists_df = pd.DataFrame()
for slug in songs_df['slug']:
    try:
        # E.T.I By Blue Öyster Cult has typo in database
        # Blue �yster Cult can't be parsed by JSON so use XML
        # Ringo response is large so use XML
        use_xml = ['eti', 'ringo']
        form = 'xml' if slug in use_xml else 'json'
        df = get_df('setlists/slug/%s' % slug, form)
        setlists_df = setlists_df.append(df)
        if len(df) == 0:
            no_live_performs.append(slug)
    except json.JSONDecodeError:
        print("Not parsed: %s" % slug)


# SONGS Dataframe
# ===============
songs_df = songs_df.reset_index().rename(columns={'@id': 'song_id',
                                                  'isoriginal': 'original'})
assert len(songs_df['slug'].unique()) == len(songs_df)
songs_df = songs_df.set_index('slug')
songs_df = songs_df.replace(r'^\s*$', np.nan, regex=True)
songs_df = songs_df.where((pd.notnull(songs_df)), None)

# fix E.T.I. Blue Öyster Cult typo from database
songs_df.at['eti', 'original_artist'] = 'Blue Öyster Cult'

# songs_df read in with XML which can't read '&' properly
# read these fields in with JSON to correct this
for song in songs_df[songs_df.name.isna()].index:
    name = get_df('songs/slug/%s' % song, 'json').at[0, 'name']
    songs_df.at[song, 'name'] = name
for song in songs_df[songs_df.original_artist.isna()].index:
    original_artist = (get_df('songs/slug/%s' % song, 'json')
                       .at[0, 'original_artist'])
    songs_df.at[song, 'original_artist'] = original_artist

songs_df = songs_df.reset_index()
songs_df = songs_df[['song_id', 'name', 'slug', 'original_artist', 'original']]
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
shows_df['showdate'] = pd.to_datetime(shows_df['showdate'], format='%Y-%m-%d')
assert len(shows_df['show_id'].unique()) == len(shows_df)
shows_df = shows_df.drop(columns='venue_id')
shows_df = shows_df.rename(columns={'venuename': 'venue_name',
                                    'showdate': 'show_date',
                                    'tourname': 'tour_name',
                                    'showorder': 'show_order'})
shows_df = shows_df.replace(r'^\s*$', np.nan, regex=True)
shows_df = shows_df.where((pd.notnull(shows_df)), None)
tmp = shows_df.merge(venues_df,
                     on=['venue_name', 'city', 'state', 'country'],
                     how='left')
shows_df = tmp[['show_id', 'show_date', 'artist', 'venue_id',
                'tour_name', 'show_order']]

# LIVE_SONGS Dataframe
#
# Note that venue_id is float because of Nan
# 1508604129 is the show_id that does not map causing this
# ====================
live_songs_df = setlists_df.rename(columns={'uniqueid': 'live_song_id',
                                            'setnumber': 'set_number',
                                            'isjamchart': 'jamchart',
                                            'soundcheck': 'sound_check',
                                            'shownotes': 'show_notes'})
assert len(live_songs_df['live_song_id'].unique()) == len(live_songs_df)
live_songs_df = live_songs_df.replace(r'^\s*$', np.nan, regex=True)
live_songs_df = live_songs_df.where((pd.notnull(live_songs_df)), None)
live_songs_df['transition'] = (live_songs_df['transition']
                               .replace(to_replace=' > ', value='>')
                               .replace(to_replace=', ', value=',')
                               .replace(to_replace='  ', value=np.nan))
live_songs_df['show_notes'] = live_songs_df['show_notes'].str.strip('\r\n')
extra_cols = (live_songs_df[['show_id', 'show_notes', 'opener', 'sound_check']]
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


# Write dataframes as pickle files
# ================================

PATH = '/tmp/atu_database'
if not os.path.exists(PATH):
    os.makedirs(PATH)
df_names = {
    'songs': songs_df,
    'shows': shows_df,
    'live_songs': live_songs_df,
    'venues': venues_df
}
for name in df_names:
    df_names[name].to_pickle(PATH + '/%s.pickle' % name)
