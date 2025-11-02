import sqlite3
print(sqlite3.sqlite_version)

db_path = r"C:\Users\Ammar.Fitwalla\Projects\nikahnama_app\nikahnama.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Rename column safely (modern SQLite)
cursor.execute("ALTER TABLE nikahnama RENAME COLUMN wali_relation TO wali_father;")

conn.commit()
conn.close()


# cursor.execute("PRAGMA table_info(nikahnama);")
# for col in cursor.fetchall():
#     print(col)
print("✅ Column renamed successfully!")
