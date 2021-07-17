import sys
import json
import pandas as pd
import pymysql.cursors
from pymysql.err import MySQLError


# TODO: better handle case when the table exists
def create_table(name, create, table, cursor):
    """Create a table in an SQL database.

    Warning: this function overrides any exisiting data!

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

    # Prepare data for SQL query
    # fillna with NULL-VALUE to be replaced by NULL later
    # ' must be replaced by '' in strings
    table = table.fillna('NULL-VALUE')
    fields = list(table.columns)
    for field in fields:
        table[field] = table[field].str.replace("'", "''")

    # Build INSERT SQL query
    fields = list(table.columns)
    cols = ', '.join(fields)
    val = ', '.join(map((lambda x: "'%%(%s)s'" % x), fields))
    rows = list(table.reset_index().iterrows())
    rows = list(map(lambda x: x[1].to_dict(), rows))
    vals = ',\n\t'.join(map(lambda x: "(%s)" % (val % x), rows))
    vals = vals.replace("'NULL-VALUE'", "NULL")
    insert = ("INSERT INTO\n"
              "\t%s(%s)\n"
              "VALUES\n"
              "\t%s;") % (name, cols, vals)

    try:
        cursor.execute(insert)
    except MySQLError as err:
        print(err)


def main(path, input_type, arg1=None, arg2=None, arg3=None, arg4=None):
    """Push the tables at the path into a SQL database."""
    # connect to database
    if input_type == "prompt":
        print("Connect to a SQL database.")
        host = input('Host: ').strip()
        database = input('Database: ').strip()
        user = input('User: ').strip()
        password = input('Password: ').strip()
    elif input_type == "arguments":
        host = arg1
        database = arg2
        user = arg3
        password = arg4
    elif input_type == "json":
        name = arg1
        with open('sql_logins/%s.json' % name) as f:
            data = json.load(f)
        host = data['host']
        database = data['database']
        user = data['user']
        password = data['password']
    else:
        raise ValueError("Inalid input type.")
    cnx = pymysql.connect(host=host,
                          database=database,
                          user=user,
                          password=password)
    print("Connected to %s as %s." % (host, user))
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
        original_artist TEXT NOT NULL,
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
        jamchart_notes TEXT
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
    for i in range(1, len(sys.argv)):
        args[i] = sys.argv[i]
    main(args[0], args[1], args[2], args[3], args[4], args[5])
