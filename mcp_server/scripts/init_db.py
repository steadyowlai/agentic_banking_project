import sqlite3
import os

# this db stores user data. it has 2 tables, one for user authentication and another for user loans.

# Use environment variable for Docker, fallback to local path for development
# This file: mcp_server/scripts/init_db.py
# Target:    mcp_server/data/database/business.db
DB_FILE = os.getenv('DB_PATH', os.path.join(os.path.dirname(__file__), '..', 'data', 'database', 'business.db'))

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
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
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
            interest_rate REAL,
            maturity_date TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # mock users
    # Format: (user_id, username, password, first_name, last_name, customer_type)
    mock_users = [
        ('usr_alice', 'alice', 'hashed_pwd_123', 'Alice', 'Johnson', 'retail'),
        ('usr_bob', 'bob', 'hashed_pwd_456', 'Bob', 'Smith', 'retail'),
        ('usr_charlie', 'charlie', 'hashed_pwd_789', 'Charlie', 'Williams', 'corporate'),
        ('usr_diana', 'diana', 'hashed_pwd_101', 'Diana', 'Martinez', 'corporate')
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', mock_users)

    # mock loans: multiple loans per user, staying within policy limits
    # Retail limit: $100,000 | Corporate limit: $10,000,000
    # Format: (loan_id, user_id, customer_type, balance, interest_rate, maturity_date, status)
    mock_loans = [
        ('LN-101', 'usr_alice', 'retail', 18500.00, 7.5, '2028-06-15', 'Active'),
        ('LN-102', 'usr_alice', 'retail', 30000.00, 8.2, '2029-03-20', 'Active'),

        ('LN-201', 'usr_bob', 'retail', 42000.00, 9.0, '2027-12-10', 'Under Review'),
        ('LN-202', 'usr_bob', 'retail', 25000.00, 7.8, '2028-08-05', 'Active'),
        ('LN-203', 'usr_bob', 'retail', 20000.00, 6.5, '2030-01-15', 'Active'),
   
        ('LN-301', 'usr_charlie', 'corporate', 2500000.00, 4.5, '2029-11-30', 'Active'),
        ('LN-302', 'usr_charlie', 'corporate', 2000000.00, 5.2, '2030-05-18', 'Active'),

        ('LN-401', 'usr_diana', 'corporate', 5400000.00, 3.8, '2028-09-22', 'Pending Approval'),
        ('LN-402', 'usr_diana', 'corporate', 2500000.00, 4.2, '2029-07-14', 'Active'),
        ('LN-403', 'usr_diana', 'corporate', 1500000.00, 5.0, '2027-10-30', 'Under Review')
    ]
    cursor.executemany('INSERT INTO loans VALUES (?, ?, ?, ?, ?, ?, ?)', mock_loans)

    conn.commit()
    conn.close()
    print("Database seeded successfully with retail and corporate customers!")

if __name__ == "__main__":
    setup_database()