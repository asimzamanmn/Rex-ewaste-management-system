import sqlite3
from flask import g
import datetime

DATABASE = "e_waste.db"

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pickups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pickup_date TEXT NOT NULL,
        address TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
''')

    # Users table with additional fields and constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Deposits table with additional fields and constraints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            location TEXT NOT NULL,
            collection_point TEXT NOT NULL,
            component TEXT NOT NULL,
            build_no TEXT,
            model_id TEXT,
            photos TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points_awarded INTEGER DEFAULT 0,
            picked_up_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create index for common queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deposits_user_id ON deposits(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    
    conn.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

def get_user_deposits(user_id):
    db = get_db()
    cursor = db.cursor()
    return cursor.execute(
        'SELECT * FROM deposits WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()

def get_user_points(user_id):
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute('SELECT points FROM users WHERE id = ?', (user_id,)).fetchone()
    return result['points'] if result else 0

def update_user_points(user_id, points):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET points = points + ? WHERE id = ?', (points, user_id))
    db.commit()