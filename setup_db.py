import sqlite3
import os

def init_db():
    db_file = 'users.db'
    if os.path.exists(db_file):
        os.remove(db_file)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
   
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
   
    users = [
        ('admin', 'password123', 'admin@example.com', 1),
        ('user1', 'pass1', 'user1@test.com', 0),
        ('user2', 'pass2', 'user2@test.com', 0)
    ]
    
    cursor.executemany('INSERT INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)', users)
    
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' initialized with {len(users)} users.")

if __name__ == "__main__":
    init_db()
