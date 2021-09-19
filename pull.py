import json
import os
import sys
import pandas as pd
import numpy as np
import atu


def main(path: str):
    """
    Pull the ATU website and download files to the given path.
    """
    songs = atu.request('songs', 'xml').set_index('slug')
    shows = atu.request('shows', 'json')
    venues = atu.request('venues', 'json')

    # special cases
    songs.at['ace-of-long-nights', 'original_artist'] = 'Motörhead/Ween'

    # songs read in with XML which can't read '&' properly
    # read these fields in with JSON to correct this
    songs = songs.replace(r'^\s*$', np.nan, regex=True)
    songs = songs.where((pd.notnull(songs)), None)
    for song in songs[songs.name.isna()].index:
        name = atu.request('songs/slug/%s' % song, 'json').at[0, 'name']
        songs.at[song, 'name'] = name
    for song in songs[songs.original_artist.isna()].index:
        original_artist = (atu.request('songs/slug/%s' % song, 'json')
                           .at[0, 'original_artist'])
        songs.at[song, 'original_artist'] = original_artist
    songs = songs.reset_index()
    songs = songs.set_index('@id')

    live_songs = pd.DataFrame()
    for slug in songs['slug']:
        try:
            # E.T.I By Blue Öyster Cult has typo in database
            # Blue �yster Cult can't be parsed by JSON so use XML
            # Ringo response is large so use XML
            use_xml = ['eti', 'ringo']
            form = 'xml' if slug in use_xml else 'json'
            df = atu.request('setlists/slug/%s' % slug, form)
            live_songs = live_songs.append(df)
        except json.JSONDecodeError:
            print("Not parsed: %s" % slug)

    # Write pickle files to the desired path
    if not os.path.exists(path):
        os.makedirs(path)
    songs.to_pickle('%s/songs.pickle' % path)
    venues.to_pickle('%s/venues.pickle' % path)
    shows.to_pickle('%s/shows.pickle' % path)
    live_songs.to_pickle('%s/live_songs.pickle' % path)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('atu_unclean')
