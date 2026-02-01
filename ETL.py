import pyodbc
import pandas as pd
from datetime import datetime

# ---------------------------
# 1️⃣ Connect to SQL Server
# working on this
# ---------------------------
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=WINDELL-35AMHC0\SQLEXPRESS;'
    r'DATABASE=churn_db;'
    r'Trusted_Connection=yes;'
)

# ---------------------------
# 2️⃣ Extract data from SQL tables
# ---------------------------
customers = pd.read_sql("SELECT * FROM customers", conn)
usage = pd.read_sql("SELECT * FROM usage", conn)
payments = pd.read_sql("SELECT * FROM payments", conn)
complaints = pd.read_sql("SELECT * FROM complaints", conn)
churn = pd.read_sql("SELECT * FROM churn", conn)

# ---------------------------
# 3️⃣ Transform data
# ---------------------------

# Convert join_date to datetime
customers['join_date'] = pd.to_datetime(customers['join_date'])

# Calculate tenure in months
customers['tenure_months'] = ((pd.Timestamp.today() - customers['join_date']).dt.days / 30).astype(int)

# Usage aggregates per customer
usage_features = usage.groupby('customer_id').agg(
    avg_monthly_minutes=('minutes_used', 'mean'),
    avg_monthly_data=('data_used_gb', 'mean'),
    avg_monthly_sms=('sms_count', 'mean')
).reset_index()

# Payments aggregates per customer
payments_features = payments.groupby('customer_id').agg(
    total_payments=('amount', 'sum'),
    avg_payment_amount=('amount', 'mean')
).reset_index()

# Complaints count per customer
complaints_features = complaints.groupby('customer_id').agg(
    num_complaints=('complaint_id', 'count')
).reset_index()

# Merge all features into a single ML-ready dataset
df = customers.merge(usage_features, on='customer_id', how='left') \
              .merge(payments_features, on='customer_id', how='left') \
              .merge(complaints_features, on='customer_id', how='left') \
              .merge(churn[['customer_id', 'is_churned']], on='customer_id', how='left')

# Fill NaN values for usage, payments, complaints
df[['avg_monthly_minutes','avg_monthly_data','avg_monthly_sms',
    'total_payments','avg_payment_amount','num_complaints']] = \
    df[['avg_monthly_minutes','avg_monthly_data','avg_monthly_sms',
        'total_payments','avg_payment_amount','num_complaints']].fillna(0)

# ---------------------------
# 4️⃣ Optional: export ML-ready dataset to CSV (for backup or Power BI)
# ---------------------------
df.to_csv("churn_ml_dataset.csv", index=False)

# ---------------------------
# 5️⃣ Output check
# ---------------------------
print("ETL complete. ML-ready dataset:")
print(df.head())

# Close SQL connection
conn.close()



import pandas as pd

df = pd.read_csv("churn_ml_dataset.csv")

print(df.head())
print(df.shape)
print(df.columns)
