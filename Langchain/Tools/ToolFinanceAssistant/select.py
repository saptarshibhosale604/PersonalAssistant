import sqlite3
import os

# Define the directory and database name
directory = '/root/Project/Rpi/PersonalAssistant/Langchain/ToolFinanceAssistant/Data'
db_name = 'db_finance.db'
db_path = os.path.join(directory, db_name)

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Query to select all data from the table
#cursor.execute('SELECT *,  ("Current Value" - "Invested Value") AS profit FROM table_test')
cursor.execute('SELECT * FROM table_investment;')
#cursor.execute("PRAGMA table_info('table_investment');")
#cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

# Fetch all rows from the executed query
rows = cursor.fetchall()

# Print the data
#print("Investment Type | Invested Value | Current Value")
print("------------------------------------------------")
for row in rows:
    print(row)
    #investment_type, invested_value, current_value = row
    #print(f"{investment_type:<15} | {invested_value:<15} | {current_value:<15}")
print("------------------------------------------------")

# Close the connection
conn.close()
