import atu
import clean
import datetime
import sql_util
from typing import Dict


LOOKBACK = 5  # days


def main(credential: sql_util.Credentials) -> str:
    """Update the SQL database."""
    cnx = credential.connect()
    cursor = cnx.cursor()
    log = ""  # maintain log to return

    def exists(id: str, table: str) -> bool:
        """Return true if the given id is in the table."""
        cursor.execute("SHOW KEYS FROM %s WHERE Key_name = 'PRIMARY'" % table)
        field = cursor.fetchone()[4]
        query = "SELECT %s FROM %s WHERE %s = %s" % (field, table, field, id)
        return bool(cursor.execute(query))

    def new_venue(row: Dict[str, str]) -> str:
        """Add the venue to the SQL database."""
        fields = ['venue_name', 'city', 'state', 'country']
        venue_id = ('-'.join([row[field].lower() for field in fields])
                    .replace(' ', '-'))
        row['venue_id'] = venue_id
        fields = ['venue_id'] + fields

        cursor.execute(sql_util.single_insert("venues", row, fields))
        print("%s added to venues." % row['venue_name'])
        log += "%s added to venues." % row['venue_name']
        return venue_id

    def new_song(row: Dict[str, str]):
        """Add the song to the SQL database."""
        fields = sql_util.get_fields('songs', cursor)
        row = row.to_dict()
        row['name'] = row['songname']
        row['original'] = row['isoriginal']
        cursor.execute(sql_util.single_insert("songs", row, fields))
        print("%s added to songs." % row['name'])
        log += "%s added to songs." % row['name']

    def add_venue_id(df: Dict[str, str]):
        """Append the venue_name field to the given dictionary."""
        query = (
            """
            SELECT *
            FROM venues
            WHERE venue_name = "%s"
            AND city = "%s"
            AND state = "%s"
            AND country = "%s"
            """ % (df['venue_name'], df['city'], df['state'], df['country']))
        if cursor.execute(query) > 0:
            result = cursor.fetchone()
            df['venue_id'] = result[0]
        else:
            df['venue_id'] = new_venue(df)
        return df

    today = datetime.datetime.now()
    deltas = [datetime.timedelta(days=i) for i in range(LOOKBACK)]
    dates = [(today - d).strftime("%Y-%m-%d") for d in deltas]

    for date in dates:
        raw_df = atu.request('shows/showdate/%s' % date, 'json')
        if len(raw_df) == 0:
            log += "no shows on %s. \n" % date
            continue  # no show on this date
        df = clean.clean_shows(raw_df)
        for index, row in df.iterrows():
            if not exists(row['show_id'], 'shows'):
                show_dict = row.to_dict()
                add_venue_id(show_dict)  # updates venues table

                # update songs table
                raw_df = atu.request('setlists/showdate/%s' % date, 'json')
                for index, row in raw_df.iterrows():
                    if not exists(row['song_id'], 'songs'):
                        new_song(row.to_dict())

                # update live_songs table
                live_songs_df = clean.clean_live_songs(raw_df)
                live_songs_df['hof'] = 0  # can't be HOF if show just occurred
                fields = sql_util.get_fields('live_songs', cursor)
                q = sql_util.multi_insert('live_songs', live_songs_df, fields)
                cursor.execute(q)

                # get these fields from live song instances
                extra_fields = (live_songs_df[['show_notes', 'opener',
                                               'sound_check']]
                                .drop_duplicates()
                                .iloc[0]
                                .to_dict())
                show_dict.update(extra_fields)

                # update shows table
                fields = sql_util.get_fields('shows', cursor)
                q = sql_util.single_insert("shows", show_dict, fields)
                cursor.execute(q)
                print("show on %s added to shows." % date)
                log += "added show on %s to the database. \n" % date
            else:
                log += "found show on %s but already in database. \n" % date

    cursor.close()
    cnx.commit()
    cnx.close()
    print('updated.')
    return log


if __name__ == "__main__":
    parser = sql_util.Credentials.argparser()
    main(sql_util.Credentials.from_args(parser.parse_args()))
