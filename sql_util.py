import json
import pandas as pd
import argparse
import pymysql.cursors
from pymysql.connections import Connection
from typing import List, Dict


class Credentials:

    def __init__(self, args):
        """Return a SQL database credentials object."""
        if args.method == "prompt":
            print("Connect to a SQL database.")
            self.host = input('Host: ').strip()
            self.database = input('Database: ').strip()
            self.user = input('User: ').strip()
            self.password = input('Password: ').strip()
        if args.method == "json":
            with open(args.json_path) as f:
                data = json.load(f)
            self.host = data['host']
            self.database = data['database']
            self.user = data['user']
            self.password = data['password']
        else:
            self.host = args.host
            self.database = args.database
            self.user = args.user
            self.password = args.password

    def argparser() -> argparse.ArgumentParser:
        """Return an argparser with arguments for credentials."""
        parser = argparse.ArgumentParser()
        parser.add_argument('--method', help="How to pass credentials")
        parser.add_argument('--host', help="Host name")
        parser.add_argument('-d', '--database', help="Name of database")
        parser.add_argument('-u', '--user', help="Name of user for login")
        parser.add_argument('-p', '--password', help="Password for user")
        parser.add_argument('--json_path', help="Json file with credentials")
        return parser

    def connect(self) -> Connection:
        """Return a connection to a MySQL server with these credentials."""
        cnx = pymysql.connect(host=self.host,
                              database=self.database,
                              user=self.user,
                              password=self.password)
        print("Connected to %s as %s." % (self.host, self.user))
        return cnx


def get_fields(name: str, cursor) -> List[str]:
    """Return the field names for the given table."""
    cursor.execute('DESCRIBE %s' % name)
    return [row[0] for row in cursor.fetchall()]


def sanitize(val: str) -> str:
    """Sanitize the string for input to a SQL query."""
    if val is None:
        return 'NULL'
    else:
        val = val.replace("'", "''")
        return val


def row_string(row: Dict[str, str], fields: List[str]) -> str:
    """Return a SQL row string for the given row."""
    values = [sanitize(str(row[field])) for field in fields]
    values = ["'%s'" % val for val in values]
    row_str = "(%s)" % ', '.join(values)
    row_str = row_str.replace("'NULL'", "NULL")
    return row_str


def single_insert(name: str, row: Dict[str, str], fields: List[str]) -> str:
    """Return a MySQL INSERT statement to insert the row into the table.

    Args:
        name (str): Name of the table to insert these rows.
        row (Dict[str, str]): Row to insert into the table.
        fields (List[str]): Fields to insert.
    """
    cols = ', '.join(fields)
    vals = row_string(row, fields)
    return ("INSERT INTO\n"
            "\t%s(%s)\n"
            "VALUES\n"
            "\t%s;") % (name, cols, vals)


def multi_insert(name: str,
                 table: pd.DataFrame,
                 fields: List[str] = None) -> str:
    """Return a MySQL INSERT statement to insert the rows of table.

    Args:
        name (str): Name of the table to insert these rows.
        table (pd.Dataframe): Pandas table of rows to be inserted.
        fields (List[str], optional): Fields to insert. Defaults to columns.
    """
    if fields is None:
        fields = list(table.columns)
    cols = ', '.join(fields)
    rows = list(table.reset_index().iterrows())
    vals = [row_string(row[1], fields) for row in rows]
    vals = ',\n\t'.join(vals)
    return ("INSERT INTO\n"
            "\t%s(%s)\n"
            "VALUES\n"
            "\t%s;") % (name, cols, vals)
