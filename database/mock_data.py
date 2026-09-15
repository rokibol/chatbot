import sqlite3
import random
from datetime import datetime, timedelta

def create_large_scale_db():
    conn = sqlite3.connect("field_nation_data.db")
    cursor = conn.cursor()

    # ১. ইউজার বা কাস্টমার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT,
            country TEXT
        )
    ''')

    # ২. সেলস বা ট্রানজেকশন টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_name TEXT,
            category TEXT,
            amount REAL,
            sale_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # ডামি ডেটা জেনারেশন (লার্জ স্কেল সিমুলেশন)
    countries = ['Bangladesh', 'USA', 'UK', 'Canada', 'Germany']
    categories = ['Electronics', 'Software', 'Hardware', 'Consulting']
    products = {
        'Electronics': ['Router', 'Switch', 'IP Camera', 'Server Rack'],
        'Software': ['SaaS Subscription', 'API License', 'Cloud Backup'],
        'Hardware': ['Fiber Cable', 'RAM Module', 'SSD Storage'],
        'Consulting': ['Data Engineering Support', 'AI Integration Consultation']
    }

    # ১০০০ জন ইউজার তৈরি করা
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        print("Creating 1,000 mock users...")
        for i in range(1, 1001):
            name = f"User_{i}"
            email = f"user{i}@fieldnation.com"
            country = random.choice(countries)
            signup_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (i, name, email, signup_date, country))

        # ৫০০০টি সেলস রেকর্ড তৈরি করা
        print("Creating 5,000 mock sales records...")
        for i in range(1, 5001):
            user_id = random.randint(1, 1000)
            category = random.choice(categories)
            product_name = random.choice(products[category])
            amount = round(random.uniform(20.0, 1500.0), 2)
            sale_date = (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?)", (i, user_id, product_name, category, amount, sale_date))

        conn.commit()
        print("Database initialized successfully with large-scale data!")
    else:
        print("Database already exists with data.")
        
    conn.close()

if __name__ == "__main__":
    create_large_scale_db()
