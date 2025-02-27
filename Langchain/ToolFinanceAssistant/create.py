import sqlite3
import os

# Define the directory and database name
directory = '/root/Project/Rpi/PersonalAssistant/Langchain/ToolFinanceAssistant/Data'
db_name = 'db_finance.db'
db_path = os.path.join(directory, db_name)

# Create the directory if it doesn't exist
os.makedirs(directory, exist_ok=True)

# Connect to the SQLite database (it will create the database if it doesn't exist)
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create the table with the specified structure
cursor.execute('''
CREATE TABLE IF NOT EXISTS table_investment (
    id INT,
    investment_type VARCHAR(50),
    investment_name VARCHAR(100),
    investment_note VARCHAR(255),
    invested_value INT,
    current_value INT
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database created and saved at: {db_path}")

