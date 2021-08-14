import sql_util
import pandas as pd
from pymysql.err import MySQLError


def main(path: str, credential: sql_util.Credentials):
    """Push the tables at the path into a SQL database."""
    cnx = credential.connect()
    cursor = cnx.cursor()

    tables = ['shows', 'songs', 'venues', 'live_songs']
    for table in tables:
        df = pd.read_pickle('%s/%s.pickle' % (path, table))
        with open('sql/create_%s.sql' % table, 'r') as f:
            query = f.read()
            try:
                cursor.execute(query)
            except MySQLError as err:
                print(err)
                cursor.execute("DROP TABLE %s;" % table)
                cursor.execute(query)
            try:
                cursor.execute(sql_util.multi_insert(table, df))
            except MySQLError as err:
                print(err)

    cursor.close()
    cnx.commit()
    cnx.close()
    print("uploaded.")


if __name__ == "__main__":
    parser = sql_util.Credentials.argparser()
    parser.add_argument('--path', help="Path to files to push to SQL database")
    args = parser.parse_args()
    main(args.path, sql_util.Credentials.from_args(args))
