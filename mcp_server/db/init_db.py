import sqlite3
import os

# this db stores user data. it has 2 tables, one for user authentication and another for user loans.
DB_FILE = "business.db"

def setup_database():
    #remove existing db file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    print(f"Creating new database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # user authentication table
    cursor.execute('''
        CREATE TABLE users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            customer_type TEXT NOT NULL
        )
    ''')

    # loan table
    cursor.execute('''
        CREATE TABLE loans (
            loan_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            customer_type TEXT NOT NULL,
            balance REAL,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # mock users
    mock_users = [
        ('usr_alice', 'alice', 'hashed_pwd_123', 'retail'),
        ('usr_bob', 'bob', 'hashed_pwd_456', 'retail'),
        ('usr_charlie', 'charlie', 'hashed_pwd_789', 'corporate'),
        ('usr_diana', 'diana', 'hashed_pwd_101', 'corporate')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', mock_users)

    # mock loans
    mock_loans = [
        ('LN-101', 'usr_alice', 'retail', 18500.00, 'Active'),
        ('LN-201', 'usr_bob', 'retail', 42000.00, 'Under Review'),
        ('LN-301', 'usr_charlie', 'corporate', 2500000.00, 'Active'),
        ('LN-401', 'usr_diana', 'corporate', 5400000.00, 'Pending Approval')
    ]
    cursor.executemany('INSERT INTO loans VALUES (?, ?, ?, ?, ?)', mock_loans)

    conn.commit()
    conn.close()
    print("Database seeded successfully with retail and corporate customers!")

if __name__ == "__main__":
    setup_database()