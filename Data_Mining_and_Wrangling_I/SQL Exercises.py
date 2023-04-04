import sqlite3
import pandas as pd
from sqlalchemy import create_engine

def create_tables():
    """
    Returns a connection to an in-memory SQLite database. The table employee
    will have the following columns:
    "full_name", "age", "rating" and "remarks"
    """

    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    return cursor.execute("""
    CREATE TABLE employee(
    full_name TEXT NOT NULL,
    age INTEGER,
    rating FLOAT NOT NULL,
    remarks TEXT
    )""")
conn = create_tables()
# Note: each RDBMS has its own way of querying the table information
res = conn.execute("PRAGMA table_info('employee')").fetchall()
conn.close()
assert_equal(len(res), 4)
assert_equal(
    [col[1]  for col in res],
    ['full_name', 'age', 'rating', 'remarks']
)

def insert_values(conn, rows):
    """
    Saves the given rows into the table "players".
    """

    conn.executemany("""INSERT INTO players VALUES (?,?,?,?) """, rows)

def append_values(conn, df):
    """
    Appends the content of data frame "df" to the "reactions" table in conn.
    """

    df.to_sql('reactions', con=conn, if_exists='append', index=False)

def read_table(db):
    """
    Reads the sqlite database file "db" and returns the contents of the
    "transactions" table as a pandas DataFrame.
    """

    conn = sqlite3.connect(db)
    df = pd.read_sql_query('SELECT * FROM transactions', conn)
    conn.close()
    return df

def stocks_more_than_5():
    """
    Returns a SQL statement that  returns the rows of the "transactions" table
    with "Quantity" greater than 5.
    Returns only the columns "StockCode", "Description" and "Quantity".
    """

    return ("""
            SELECT StockCode, Description, Quantity
            FROM transactions
            WHERE Quantity > 5
            """)

def get_invoices():
    """
    Returns a SQL statement that returns the reows of the "transactions" table
    grouped by "InvoiceNo" with the following columns: "InvoiceNo",
    "ItemCount", and "TotalQuantity".
    """

    return ("""
            SELECT InvoiceNo, COUNT(InvoiceNo) AS ItemCount,
                SUM(Quantity) AS TotalQuantity
            FROM transactions
            GROUP BY InvoiceNo
            ORDER BY ItemCount DESC
            """)

def white_department(conn):
    """
    The functions functions accepts a SQLAlchemy connection and returns a
    pandas Series.
    """

    sql ='''SELECT department_id, count(*) AS row_counter
            FROM products
            WHERE product_name LIKE 'White %'
            GROUP BY department_id
            ORDER BY row_counter DESC
          '''

    return pd.read_sql(sql, con=conn, index_col='department_id').squeeze()

def count_aisle_products(conn):
    """
    The functions accepts a SQLAlchemy connection and returns a
    pandas DataFrame. It has the following columns:
    "aisle_id", "aisle" and "product_count".
    """

    return pd.read_sql(
        """
        SELECT p.aisle_id, a.aisle, COUNT(p.product_id) AS product_count
        FROM products p
        JOIN aisles a
        ON p.aisle_id = a.aisle_id
        GROUP BY p.aisle_id
        HAVING product_count < 100
        ORDER BY product_count
        """, conn)

def concat_cols(conn):
    """
    Accepts an SQLAlchemy connection and sets the value of "col3" for rows
    with even "col2" to the concatenation of "col1" and "col2".
    """

    return conn.execute(
            '''
            UPDATE cols
            SET col3 = col1 || col2
            WHERE col2 % 2 = 0
            ''')

def del_row(conn):
    """
    The functions accepts a SQLAlchemy connection and deteles rows with a
    "col1" value of "d".
    """

    conn.execute(
        """
        DELETE FROM cols
        WHERE col1 = 'd'
        """)

