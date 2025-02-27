import sqlite3
import os
from datetime import date

# Define the directory and database name

directory = '/root/Project/Rpi/PersonalAssistant/Langchain/ToolFinanceAssistant/Data'
db_name = 'db_finance.db'
db_path = os.path.join(directory, db_name)

# Connect to the SQLite database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()


# Sample data to insert
data = [
    (1, 'Physical', 'Gold Investment', 'Invested in physical gold', 7100, 7100),
    (2, 'Stocks', 'Tech Stocks', 'Invested in technology sector', 45800, 49100),
    (3, 'MF', 'Equity Mutual Fund', 'Invested in equity mutual funds', 75000, 87600),
    (4, 'FD', 'Fixed Deposit', 'Bank fixed deposit', 120000, 120000),
    (5, 'Saving', 'Savings Account', 'Regular savings account', 14800, 14800)
]

# Insert the data into the table
cursor.executemany('''
    INSERT INTO table_investment (id, investment_type, investment_name, investment_note, invested_value, current_value)
    VALUES (?, ?, ?, ?, ?, ?)
''', data)

print("data inserted")
# Close the connection
conn.close()
