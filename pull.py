import json
import os
import sys
import pandas as pd
import atu


def main(path: str):
    """
    Pull the ATU website and download files to the given path.
    """
    songs = atu.request('songs', 'xml').set_index('@id')
    shows = atu.request('shows', 'json')
    venues = atu.request('venues', 'json')

    # Some songs in songs_df do not have live performaces
    # for one of the following reasons:
    #  - In the discography with no live performace
    #  - Appears as a tease/jam without its own entry in a set
    # This list keeps track of songs that fall in this category
    no_live_performs = []

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
            if len(df) == 0:
                no_live_performs.append(slug)
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
