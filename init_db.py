import sqlite3

# Connect to SQLite database (creates app.db if it doesn't exist)
conn = sqlite3.connect("app.db")
cur = conn.cursor()

# Users table: stores name, email, and credits
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    credits INTEGER DEFAULT 0
)
""")

# Verses table: optional, if you want to move verses from .txt into DB
cur.execute("""
CREATE TABLE IF NOT EXISTS verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book TEXT,
    chapter INTEGER,
    verse INTEGER,
    text TEXT,
    translation TEXT
)
""")

conn.commit()
conn.close()

print("Database setup complete! Tables created.")
