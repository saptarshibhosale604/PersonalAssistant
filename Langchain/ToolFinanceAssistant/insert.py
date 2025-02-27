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
    ('Physical', 'Gold Investment', 'Invested in physical gold', date(2023, 1, 15), 7100, 7100),
    ('Stock', 'Tech Stocks', 'Invested in technology sector', date(2023, 2, 20), 45800, 49100),
    ('MF', 'Equity Mutual Fund', 'Invested in equity mutual funds', date(2023, 3, 10), 75000, 87600),
    ('FD', 'Fixed Deposit', 'Bank fixed deposit', date(2023, 4, 5), 120000, 120000),
    ('Saving', 'Savings Account', 'Regular savings account', date(2023, 5, 1), 14800, 14800)
]

# Insert the data into the table
cursor.executemany('''
    INSERT INTO table_investment (investment_type, investment_name, investment_note, investment_date, invested_value, current_value)
    VALUES (?, ?, ?, ?, ?, ?)
''', data)




# Commit the changes to permanently store them in the database
conn.commit()


print("data inserted")

# Close the connection
conn.close()
