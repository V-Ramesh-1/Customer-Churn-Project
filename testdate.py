import pyodbc

# -----------------------------
# 1. Correct server & database
# -----------------------------
server = r'WINDELL-35AMHC0\SQLEXPRESS'  # use raw string to escape backslash
database = 'churn_db'

# -----------------------------
# 2. Establish connection
# -----------------------------
try:
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("Connection successful! Test query result:", cursor.fetchone())

except pyodbc.Error as e:
    print("Error connecting to SQL Server:")
    print(e)
