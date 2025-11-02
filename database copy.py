# database.py
import sqlite3
from datetime import datetime

DB_PATH = "nikahnama.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS nikahnama (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          serial_no TEXT,
          reg_no TEXT,
          masjid_name TEXT,

          hijri_date TEXT,
          eng_date TEXT,
          nikah_time TEXT,
          place_of_nikah TEXT,

          groom_name TEXT,
          groom_father TEXT,
          groom_age INTEGER,
          groom_status TEXT,
          groom_address TEXT,

          bride_name TEXT,
          bride_father TEXT,
          bride_age INTEGER,
          bride_status TEXT,
          bride_address TEXT,

          wali_name TEXT,
          wali_age INTEGER,
          wali_relation TEXT,
          wali_address TEXT,

          witness1_name TEXT,
          witness1_father TEXT,
          witness1_age INTEGER,
          witness1_address TEXT,

          witness2_name TEXT,
          witness2_father TEXT,
          witness2_age INTEGER,
          witness2_address TEXT,

          mahr_words TEXT,
          mahr_figure TEXT,

          qazi_name TEXT,
          qazi_certificate TEXT,

          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def insert_record(data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cols = ", ".join(data.keys())
    params = ", ".join([":" + k for k in data.keys()])
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    sql = f"INSERT INTO nikahnama ({cols}, updated_at) VALUES ({params}, :updated_at)"
    cur.execute(sql, data)
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid

def update_record(rec_id: int, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    data["updated_at"] = datetime.now().isoformat(timespec="seconds")
    set_sql = ", ".join([f"{k}=:{k}" for k in data.keys()])
    sql = f"UPDATE nikahnama SET {set_sql}, updated_at=:updated_at WHERE id=:id"
    data["id"] = rec_id
    cur.execute(sql, data)
    conn.commit()
    conn.close()

def delete_record(rec_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM nikahnama WHERE id=?", (rec_id,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM nikahnama ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
