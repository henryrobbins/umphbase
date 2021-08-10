import sys
import pandas as pd
import argparse
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


def main(path, method, host=None, database=None, username=None,
         password=None, json_path=None):
    """Push the tables at the path into a SQL database."""
    cnx = sql_util.connect(method, host=host, database=database, user=username,
                           password=password, json_path=json_path)
    cursor = cnx.cursor()

    shows = pd.read_pickle('%s/shows.pickle' % path)
    with open('sql/create_shows.sql', 'r') as f:
        query = f.read()
        create_table('shows', query, shows, cursor)

    songs = pd.read_pickle('%s/songs.pickle' % path)
    with open('sql/create_songs.sql', 'r') as f:
        query = f.read()
        create_table('songs', query, songs, cursor)

    venues = pd.read_pickle('%s/venues.pickle' % path)
    with open('sql/create_venues.sql', 'r') as f:
        query = f.read()
        create_table('venues', query, venues, cursor)

    live_songs = pd.read_pickle('%s/live_songs.pickle' % path)
    with open('sql/create_live_songs.sql', 'r') as f:
        query = f.read()
        create_table('live_songs', query, live_songs, cursor)

    cursor.close()
    cnx.commit()
    cnx.close()
    print("uploaded.")


# TODO: Update README to reflect argparse change
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help="Path to files to push to SQL database")
    parser.add_argument('--method', help="How to pass database credentials")
    parser.add_argument('--host', help="Host name")
    parser.add_argument('-d', '--database', help="Name of database")
    parser.add_argument('-u', '--username', help="Username for login")
    parser.add_argument('-p', '--password', help="Password for user")
    parser.add_argument('--json', help="Path to json file with credentials")
    args = parser.parse_args()

    main(path=args.path,
         method=args.method,
         host=args.host,
         database=args.database,
         username=args.username,
         password=args.password,
         json_path=args.json)
