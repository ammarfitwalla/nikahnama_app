# import sqlite3
# from datetime import datetime

# # Database path
# db_path = r"C:\Users\Ammar.Fitwalla\Projects\nikahnama_app\nikahnama_app\nikahnama.db"

# # Define table and columns
# DB_COLUMNS = [
#     "id", "serial_no", "reg_no", "masjid_name",
#     "hijri_date", "eng_date", "nikah_time", "place_of_nikah",
#     "groom_name", "groom_father", "groom_age", "groom_address",
#     "bride_name", "bride_father", "bride_age", "bride_address",
#     "wali_name", "wali_age", "wali_father", "wali_address",
#     "witness1_name", "witness1_father", "witness1_age", "witness1_address",
#     "witness2_name", "witness2_father", "witness2_age", "witness2_address",
#     "mahr_words", "mahr_figure", "qazi_name",
#     "created_at", "updated_at",
# ]

# # Dummy data tuple (values must match column order)
# dummy_record = (
#     2, "SN-001", "REG-2025", "Masjid Al-Noor",
#     "1447-08-15", "2025-10-29", "6:30 PM", "Karachi",
#     "Ahmed Khan", "Mohammad Khan", 28, "Karachi, Pakistan",
#     "Ayesha Bibi", "Abdul Rehman", 25, "Karachi, Pakistan",
#     "Hassan Ali", 50, "Ibrahim Ali", "Karachi, Pakistan",
#     "Imran Qureshi", "Latif Qureshi", 35, "Karachi, Pakistan",
#     "Sohail Ahmed", "Nadeem Ahmed", 33, "Karachi, Pakistan",
#     "Fifty thousand rupees", 50000, "Mufti Saeed",
#     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# )

# # Connect to database
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# # Build SQL dynamically
# columns_str = ", ".join(DB_COLUMNS)
# placeholders = ", ".join(["?" for _ in DB_COLUMNS])
# sql = f"INSERT INTO nikahnama ({columns_str}) VALUES ({placeholders})"

# # Insert the record
# cursor.execute(sql, dummy_record)
# conn.commit()
# conn.close()

# print("✅ Dummy data inserted successfully!")

import sqlite3
import random
from datetime import datetime, timedelta

# === CONFIG ===
db_path = r"C:\Users\Ammar.Fitwalla\Projects\nikahnama_app\nikahnama_app\nikahnama.db"
num_records = 10  # 🔢 how many dummy entries you want

# === COLUMNS (must match DB schema) ===
DB_COLUMNS = [
    "serial_no", "reg_no", "masjid_name",
    "hijri_date", "eng_date", "nikah_time", "place_of_nikah",
    "groom_name", "groom_father", "groom_age", "groom_address",
    "bride_name", "bride_father", "bride_age", "bride_address",
    "wali_name", "wali_age", "wali_father", "wali_address",
    "witness1_name", "witness1_father", "witness1_age", "witness1_address",
    "witness2_name", "witness2_father", "witness2_age", "witness2_address",
    "mahr_words", "mahr_figure", "qazi_name",
    "created_at", "updated_at",
]

# === SAMPLE DATA SETS ===
masjids = [
    "Masjid Ahle Hadees, Kurla",
    "Masjid Al-Noor, Bandra",
    "Masjid Al-Falah, Andheri",
    "Masjid Usman Ghani, Jogeshwari",
]

places = [
    "Kurla West, Mumbai 400070",
    "Andheri East, Mumbai 400059",
    "Bandra West, Mumbai 400050",
    "Byculla East, Mumbai 400027",
]

first_names = ["Mohammed", "Yusuf", "Imran", "Abdul", "Anees", "Sohail", "Zubair"]
fathers = ["Kareem", "Majid", "Rahman", "Hafeez", "Rehman", "Ahmed"]
surnames = ["Al-Farouqi", "Shaikh", "Qureshi", "Ansari", "Khan", "Siddiqui"]

bride_names = ["Ayesha", "Fatima", "Zainab", "Khadija", "Maryam", "Sumaiya", "Asma"]
bride_fathers = ["Ahmed", "Rahman", "Latif", "Yusuf", "Nadeem"]

qazis = ["Qazi Abdul Rahman", "Mufti Saeed", "Qazi Imran Farooqi", "Maulana Iqbal Husain"]

mahr_amounts = [
    ("Fifty Thousand Indian Rupees only", 50000),
    ("Seventy-Five Thousand Indian Rupees only", 75000),
    ("One Lakh Indian Rupees only", 100000),
    ("One Lakh Twenty-Five Thousand Indian Rupees only", 125000),
]

# === FUNCTION TO GENERATE RANDOM DATE ===
def random_date():
    base_date = datetime(2025, 1, 1)
    random_days = random.randint(0, 300)
    date = base_date + timedelta(days=random_days)
    hijri_date = f"1447-{random.randint(1, 12):02d}-{random.randint(1, 29):02d}"
    return hijri_date, date.strftime("%d-%b-%Y"), date.strftime("%I:%M %p")

# === FUNCTION TO GENERATE A RECORD ===
def make_record(serial):
    hijri, eng_date, time_str = random_date()
    groom_first = random.choice(first_names)
    groom_father = random.choice(fathers)
    groom_last = random.choice(surnames)

    bride_first = random.choice(bride_names)
    bride_father = random.choice(bride_fathers)
    bride_last = random.choice(surnames)

    wali_father = random.choice(fathers)
    witness1_father = random.choice(fathers)
    witness2_father = random.choice(fathers)

    mahr_words, mahr_figure = random.choice(mahr_amounts)

    masjid = random.choice(masjids)
    place = random.choice(places)
    qazi = random.choice(qazis)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"{serial:05d}",  # serial_no
        f"REG-{2025}-{serial:04d}",  # reg_no
        masjid,
        hijri,
        eng_date,
        time_str,
        place,
        f"{groom_first} {groom_last}",
        f"{groom_father} {groom_last}",
        random.randint(25, 35),
        f"{random.randint(1,99)} Main Road, {place}",
        f"{bride_first} {bride_last}",
        f"{bride_father} {bride_last}",
        random.randint(20, 30),
        f"House No. {random.randint(1,200)}, {place}",
        f"{bride_father} {bride_last}",
        random.randint(45, 60),
        f"Late {wali_father} {bride_last}",
        f"House No. {random.randint(1,200)}, {place}",
        f"Yusuf {random.choice(surnames)}",
        f"{witness1_father} {random.choice(surnames)}",
        random.randint(30, 50),
        f"Flat No. {random.randint(1,50)}, {place}",
        f"Imran {random.choice(surnames)}",
        f"{witness2_father} {random.choice(surnames)}",
        random.randint(30, 45),
        f"House No. {random.randint(1,100)}, {place}",
        mahr_words,
        mahr_figure,
        qazi,
        now,
        now,
    )

# === MAIN INSERTION ===
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns_str = ", ".join(DB_COLUMNS)
placeholders = ", ".join(["?" for _ in DB_COLUMNS])
sql = f"INSERT INTO nikahnama ({columns_str}) VALUES ({placeholders})"

for i in range(1, num_records + 1):
    record = make_record(i)
    cursor.execute(sql, record)

conn.commit()
conn.close()

print(f"✅ Inserted {num_records} dummy nikahnama records successfully!")
