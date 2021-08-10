import json
import pandas as pd
import pymysql.cursors
from pymysql.connections import Connection
from typing import List, Dict


def connect(method: str,
            host: str = None,
            database: str = None,
            user: str = None,
            password: str = None,
            json_path: str = None) -> Connection:
    """Return a connection to a MySQL server.

    Args:
        method (str): {"args", "prompt", "json"}
        host (str, optional): Host where the database server is located.
        database (str, optional): Database to use.
        user (str, optional): Username to log in as.
        password (str, optional): Password to use.
        json_path (str, optional): Path to JSON file with connection info.

    Returns:
        Connection: A connection to a MySQL database
    """
    if method == "prompt":
        print("Connect to a SQL database.")
        host = input('Host: ').strip()
        database = input('Database: ').strip()
        user = input('User: ').strip()
        password = input('Password: ').strip()
    if method == "json":
        with open(json_path) as f:
            data = json.load(f)
        host = data['host']
        database = data['database']
        user = data['user']
        password = data['password']
    cnx = pymysql.connect(host=host,
                          database=database,
                          user=user,
                          password=password)
    print("Connected to %s as %s." % (host, user))
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
