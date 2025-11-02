# constants.py

# all DB columns in the table order we show in the grid
DB_COLUMNS = [
    "id", "serial_no", "reg_no", "masjid_name",
    "hijri_date", "eng_date", "nikah_time", "place_of_nikah",
    "groom_name", "groom_father", "groom_age", "groom_address",
    "bride_name", "bride_father", "bride_age", "bride_address",
    "wali_name", "wali_age", "wali_father", "wali_address",
    "witness1_name", "witness1_father", "witness1_age", "witness1_address",
    "witness2_name", "witness2_father", "witness2_age", "witness2_address",
    "mahr_words", "mahr_figure", "qazi_name",
    "created_at", "updated_at",
]

HEADERS = [c.replace("_", " ").title() for c in DB_COLUMNS]

# fields that must not be empty on save
REQUIRED_FIELDS = [
    "groom_name",
    "bride_name",
    "eng_date",
    "place_of_nikah",
    "witness1_name",
    "mahr_words",
]
