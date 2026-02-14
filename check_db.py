import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Tables:", tables)

# Show columns in users table
cur.execute("PRAGMA table_info(users);")
print("Users table columns:", cur.fetchall())

# Show columns in verses table
cur.execute("PRAGMA table_info(verses);")
print("Verses table columns:", cur.fetchall())

conn.close()
