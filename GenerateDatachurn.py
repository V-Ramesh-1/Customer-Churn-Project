import pyodbc
import random
from faker import Faker

fake = Faker()

# 1️⃣ Connect to SQL Server
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=WINDELL-35AMHC0\SQLEXPRESS;'
    r'DATABASE=churn_db;'
    r'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# 2️⃣ Generate 1000 customers
NUM_CUSTOMERS = 1000
customers = []
for _ in range(NUM_CUSTOMERS):
    gender = random.choice(["Male", "Female"])
    age = random.randint(18, 70)
    first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
    customers.append((
        first_name,
        fake.last_name(),
        gender,
        age,
        fake.email(),
        fake.address().replace("\n", ", "),
        fake.phone_number(),
        random.choice(["Prepaid", "Postpaid"]),
        fake.date_between(start_date='-3y', end_date='today')
    ))

cursor.executemany("""
    INSERT INTO customers
    (first_name, last_name, gender, age, email, address, phone, plan_type, join_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", customers)
conn.commit()
print(f"Inserted {NUM_CUSTOMERS} customers.")

# 3️⃣ Get customer IDs
cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# 4️⃣ Generate usage data
usage_rows = []
for cid in customer_ids:
    for _ in range(random.randint(5, 15)):
        usage_rows.append((
            cid,
            random.randint(50, 300),   # minutes_used
            random.randint(1, 10),     # data_used_gb
            random.randint(10, 50),    # sms_count
            fake.date_between(start_date='-1y', end_date='today')  # usage_date
        ))

cursor.executemany("""
    INSERT INTO usage
    (customer_id, minutes_used, data_used_gb, sms_count, usage_date)
    VALUES (?, ?, ?, ?, ?)
""", usage_rows)
conn.commit()
print("Inserted usage data.")

# 5️⃣ Generate payments data
payments_rows = []
for cid in customer_ids:
    for _ in range(random.randint(4, 8)):
        payments_rows.append((
            cid,
            round(random.uniform(10, 100), 2),  # amount
            random.choice(["Credit Card", "Debit Card", "Online Transfer"]),
            fake.date_between(start_date='-1y', end_date='today')  # payment_date
        ))

cursor.executemany("""
    INSERT INTO payments
    (customer_id, amount, payment_method, payment_date)
    VALUES (?, ?, ?, ?)
""", payments_rows)
conn.commit()
print("Inserted payments data.")

# 6️⃣ Generate complaints data
complaints_rows = []
for cid in customer_ids:
    for _ in range(random.randint(0, 3)):
        complaints_rows.append((
            cid,
            random.choice(["Network Issue", "Billing Issue", "Slow Internet", "Poor Service"]),
            fake.date_between(start_date='-1y', end_date='today'),  # complaint_date
            random.choice(["Open", "Closed"])  # status
        ))

cursor.executemany("""
    INSERT INTO complaints
    (customer_id, complaint_type, complaint_date, status)
    VALUES (?, ?, ?, ?)
""", complaints_rows)
conn.commit()
print("Inserted complaints data.")

# 7️⃣ Generate churn data
churn_rows = []
for cid in customer_ids:
    is_churned = random.choices([0, 1], weights=[0.8, 0.2])[0]  # 20% churn
    churn_date = fake.date_between(start_date='-6m', end_date='today') if is_churned else None
    churn_rows.append((cid, is_churned, churn_date))

cursor.executemany("""
    INSERT INTO churn
    (customer_id, is_churned, churn_date)
    VALUES (?, ?, ?)
""", churn_rows)
conn.commit()
print("Inserted churn data.")

# 8️⃣ Close connection
conn.close()
print("Full extended churn dataset inserted successfully!")
