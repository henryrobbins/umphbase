import sys
import pandas as pd
import sql_util
from pymysql.err import MySQLError


# TODO: better handle case when the table exists
def create_table(name, create, table, cursor):
    """Create a table in an SQL database.

    Warning: this function overrides any existing data!

    Attributes:
        name (str): Name of the table
        create (str): SQL statement for creating the table
        table (pd.DataFrame): The table to be added
        cursor (MySQLCursor): Cursor for MySQL database
    """
    try:
        cursor.execute(create)
    except MySQLError as err:
        print(err)
        cursor.execute("DROP TABLE %s;" % name)
        cursor.execute(create)

    try:
        cursor.execute(sql_util.multi_insert(name, table))
    except MySQLError as err:
        print(err)


def main(path, method, arg1=None, arg2=None, arg3=None, arg4=None):
    """Push the tables at the path into a SQL database."""
    # connect to database
    if method == 'prompt':
        cnx = sql_util.connect(method)
    elif method == 'args':
        cnx = sql_util.connect(method, host=arg1, database=arg2,
                               user=arg3, password=arg4)
    elif method == 'json':
        cnx = sql_util.connect(method, json_path=arg1)
    else:
        raise ValueError("Inalid input type.")
    cursor = cnx.cursor()

    # =================================================
    # shows
    # =================================================

    shows = pd.read_pickle('%s/shows.pickle' % path)
    shows['show_date'] = shows['show_date'].astype(str)

    create_shows = """
    CREATE TABLE shows (
        show_id BIGINT PRIMARY KEY,
        show_date DATE NOT NULL,
        show_order TEXT NOT NULL,
        artist TEXT NOT NULL,
        venue_id TEXT NOT NULL,
        tour_name TEXT NOT NULL,
        show_notes LONGTEXT,
        opener TEXT,
        sound_check LONGTEXT
    );
    """

    create_table('shows', create_shows, shows, cursor)

    # =================================================
    # songs
    # =================================================

    songs = pd.read_pickle('%s/songs.pickle' % path)

    create_songs = """
    CREATE TABLE songs (
        song_id INT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT NOT NULL,
        original_artist TEXT,
        original BOOLEAN NOT NULL
    );
    """

    create_table('songs', create_songs, songs, cursor)

    # =================================================
    # venues
    # =================================================

    venues = pd.read_pickle('%s/venues.pickle' % path)

    create_venues = """
    CREATE TABLE venues (
        venue_id TEXT NOT NULL,
        venue_name TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT,
        country TEXT NOT NULL
    );
    """

    create_table('venues', create_venues, venues, cursor)

    # =================================================
    # live_songs
    # =================================================

    live_songs = pd.read_pickle('%s/live_songs.pickle' % path)

    create_live_songs = """
    CREATE TABLE live_songs (
        live_song_id BIGINT PRIMARY KEY,
        show_id BIGINT NOT NULL,
        song_id INT NOT NULL,
        set_number TEXT NOT NULL,
        position INT NOT NULL,
        transition TEXT,
        footnote TEXT,
        jamchart BOOLEAN NOT NULL,
        jamchart_notes TEXT,
        parent BOOLEAN NOT NULL,
        hof BOOLEAN NOT NULL
    );
    """

    create_table('live_songs', create_live_songs, live_songs, cursor)

    # commit changes and close connection
    cursor.close()
    cnx.commit()
    cnx.close()
    print("Updated.")


if __name__ == "__main__":
    args = {i: None for i in range(6)}
    for i in range(0, len(sys.argv) - 1):
        args[i] = sys.argv[i + 1]
    main(args[0], args[1], args[2], args[3], args[4], args[5])
