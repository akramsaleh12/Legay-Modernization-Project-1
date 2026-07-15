import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("employee_table.db")

# Read ALL columns from the table
df = pd.read_sql_query("SELECT * FROM employee_table;", conn)

# Display the full table
print(df.to_string(index=False))

conn.close()
