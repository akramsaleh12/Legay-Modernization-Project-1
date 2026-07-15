import sqlite3

# ---------------------------------------------------------
# Connect to SQLite database (creates file if not exists)
# ---------------------------------------------------------
conn = sqlite3.connect("employee_table.db")
cursor = conn.cursor()

# ---------------------------------------------------------
# Create employee_table
# ---------------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS employee_table (
    emp_num                 INTEGER PRIMARY KEY,
    emp_name                TEXT NOT NULL,
    emp_basic_salary        REAL NOT NULL,
    housing_allowance       REAL NOT NULL,
    transportation_allowance REAL NOT NULL,
    tax                     REAL NOT NULL,
    insurance               REAL NOT NULL,
    tot_income              REAL NOT NULL,
    tot_deductions          REAL NOT NULL,
    net_salary              REAL NOT NULL,
    date                    TEXT NOT NULL
);
""")

print("employee_table created successfully.")

# ---------------------------------------------------------
# Optional: Insert sample rows
# ---------------------------------------------------------
sample_rows = [
    (1, "John Smith", 5000.00, 1500.00, 600.00, 400.00, 200.00, 7100.00, 1000.00, 6100.00, "2026-07-01"),
    (2, "Sara Johnson", 6200.00, 1800.00, 700.00, 500.00, 250.00, 8700.00, 1250.00, 7450.00, "2026-07-01"),
    (3, "Michael Brown", 4500.00, 1200.00, 550.00, 350.00, 180.00, 6250.00, 880.00, 5370.00, "2026-07-01"),
]

cursor.executemany("""
INSERT INTO employee_table (
    emp_num, emp_name, emp_basic_salary, housing_allowance,
    transportation_allowance, tax, insurance, tot_income,
    tot_deductions, net_salary, date
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", sample_rows)

conn.commit()
print("Sample rows inserted.")

# ---------------------------------------------------------
# Close connection
# ---------------------------------------------------------
conn.close()
