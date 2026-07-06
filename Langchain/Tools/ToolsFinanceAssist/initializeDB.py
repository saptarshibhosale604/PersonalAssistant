import sqlite3

# Connect to the SQLite database
database = 'Data/Assets.db'
# database = 'Langchain/Tools/ToolsFinanceAssist/Data/Assets.db'

print("Initialise script")

def CreateTable():
    print("CreateTable()")

    conn = sqlite3.connect(database)
    # Create a cursor object
    cur = conn.cursor()

    # Create the assets table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS assetsSummary (
            SrNo INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            InvestedAmount REAL NOT NULL,
            CurrentAmount REAL NOT NULL,
            Profit REAL NOT NULL
        );
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def InsertIntoTable():

    print("InsertIntoTable()")

    conn = sqlite3.connect(database)
    # Create a cursor object
    cur = conn.cursor()

    # Insert sample data into the assets table
    cur.execute("""
        INSERT INTO assetsSummary (SrNo, Name, InvestedAmount, CurrentAmount, Profit)
        VALUES
            (1, 'Asset 1', 10000.0, 5000.0, 3000.0),
            (2, 'Asset 2', 20000.0, 10000.0, 8000.0),
            (3, 'Asset 3', 15000.0, 7500.0, 6000.0),
            (4, 'Asset 4', 25000.0, 12500.0, 9000.0),
            (5, 'Asset 5', 30000.0, 17500.0, 10000.0)
    """)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def SelectFromTable():
    print("SelectFromTable()")

    conn = sqlite3.connect(database)
    # Create a cursor object
    cur = conn.cursor()

    # Insert sample data into the assets table
    cur.execute("""
        SELECT * FROM assetsSummary
    """)

    # Fetch all rows from the query result
    rows = cur.fetchall()

    # Print each row as a tuple (default behavior)
    for row in rows:
        print(row)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

userQuery = ""

def UserInputSelectSQL():
    print("SelectFromTable()")

    conn = sqlite3.connect(database)
    # Create a cursor object
    cur = conn.cursor()

    global userQuery

    print("table: assetsSummary")
    userQuery = input("SELECT sql query: ")

    if userQuery == "":
        userQuery = "SELECT * FROM assetsSummary"

    # select data from the assets table
    cur.execute(userQuery)

    # Fetch all rows from the query result
    rows = cur.fetchall()

    # Print each row as a tuple (default behavior)
    for row in rows:
        print(row)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
# CreateTable()
# InsertIntoTable()
# SelectFromTable()
UserInputSelectSQL()
