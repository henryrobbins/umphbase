import sql_util
import pandas as pd
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


def main(path: str, credential: sql_util.Credentials):
    """Push the tables at the path into a SQL database."""
    cnx = credential.connect()
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
    parser = sql_util.Credentials.argparser()
    parser.add_argument('--path', help="Path to files to push to SQL database")
    args = parser.parse_args()
    main(args.path, sql_util.Credentials(args))
