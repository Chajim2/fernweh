# db.py
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3

# Check if extensions are supported
try:
    conn = sqlite3.connect(':memory:')
    conn.enable_load_extension(True)
    print("✅ Extensions supported!")
except AttributeError:
    print("❌ Extensions NOT supported - need pysqlite3-binary")