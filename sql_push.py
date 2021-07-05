import sys
import json
import pandas as pd
import mysql.connector


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
    except mysql.connector.Error as err:
        print(err)
        cursor.execute("DROP TABLE %s;" % name)
        cursor.execute(create)

    cols = ', '.join(list(table.columns))
    vals = ', '.join(map((lambda x: '%%(%s)s' % x), list(table.columns)))
    insert = """INSERT INTO %s
    (%s)
    VALUES (%s)
    """ % (name, cols, vals)

    for row in table.reset_index().iterrows():
        data = row[1].to_dict()
        try:
            cursor.execute(insert, data)
        except mysql.connector.Error as err:
            print(data)
            print(err)


# connect to database
if len(sys.argv) > 1:
    name = sys.argv[1]
    with open('sql_logins/%s.json' % name) as f:
        data = json.load(f)
    host = data['host']
    user = data['user']
    password = data['password']
else:
    print("Connect to a SQL database.")
    host = input('Host: ').strip()
    user = input('User: ').strip()
    password = input('Password: ').strip()
cnx = mysql.connector.connect(host=host,
                              database='umphbase',
                              user=user,
                              password=password)
print("Connected to %s as %s." % (host, user))
cursor = cnx.cursor()

# =================================================
# shows
# =================================================

shows = pd.read_pickle('atu_database/shows.pickle')
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

songs = pd.read_pickle('atu_database/songs.pickle')

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

venues = pd.read_pickle('atu_database/venues.pickle')

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

live_songs = pd.read_pickle('atu_database/live_songs.pickle')

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
