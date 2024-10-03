import sqlite3

DATABASE_PATH = 'payments.db'

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            username TEXT,
            timestamp INTEGER,
            tickets INTEGER,
            screenshot_path TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
