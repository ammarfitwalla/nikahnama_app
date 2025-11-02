# ui/nikah_form.py
from PyQt5 import QtCore, QtWidgets
import re

class NikahForm(QtWidgets.QWidget):
    """
    Two-column Nikahnama form.
    - Small inputs arranged side-by-side (max 3 per row) within each column.
    - Address/long fields stay full-width (within their column).
    - Public API unchanged: get_data(), set_data(dict), clear()
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    # ---------- UI BUILD ----------
    def _build(self):
        # Top-level layout
        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.setSpacing(12)

        # Columns container (single page with two side-by-side columns)
        cols_hbox = QtWidgets.QHBoxLayout()
        cols_hbox.setSpacing(12)

        # Left column
        self.left_col = QtWidgets.QWidget()
        self.left_vbox = QtWidgets.QVBoxLayout(self.left_col)
        self.left_vbox.setSpacing(12)

        # Right column
        self.right_col = QtWidgets.QWidget()
        self.right_vbox = QtWidgets.QVBoxLayout(self.right_col)
        self.right_vbox.setSpacing(12)

        cols_hbox.addWidget(self.left_col, 1)
        cols_hbox.addWidget(self.right_col, 1)

        # --------- Widgets (create once; register for data I/O) ---------
        # header
        self.serial_no = QtWidgets.QLineEdit()
        self.reg_no = QtWidgets.QLineEdit()
        self.masjid_name = QtWidgets.QLineEdit("Masjid Ahle Hadees, Kurla")

        # event
        self.hijri_date = QtWidgets.QLineEdit()
        self.eng_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate()); self.eng_date.setCalendarPopup(True)
        self.nikah_time = QtWidgets.QTimeEdit(QtCore.QTime.currentTime())
        self.place_of_nikah = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.place_of_nikah)

        # groom
        self.groom_name = QtWidgets.QLineEdit()
        self.groom_father = QtWidgets.QLineEdit()
        self.groom_age = QtWidgets.QSpinBox(); self.groom_age.setRange(0, 120); self.groom_age.setValue(25)
        # self.groom_status = QtWidgets.QComboBox(); self.groom_status.addItems(["", "Unmarried", "Married", "Divorced", "Widower"])
        self.groom_address = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.groom_address)

        # bride
        self.bride_name = QtWidgets.QLineEdit()
        self.bride_father = QtWidgets.QLineEdit()
        self.bride_age = QtWidgets.QSpinBox(); self.bride_age.setRange(0, 120); self.bride_age.setValue(23)
        # self.bride_status = QtWidgets.QComboBox(); self.bride_status.addItems(["", "Unmarried", "Married", "Divorced", "Widow"])
        self.bride_address = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.bride_address)

        # wali
        self.wali_name = QtWidgets.QLineEdit()
        self.wali_age = QtWidgets.QSpinBox(); self.wali_age.setRange(0, 120)
        self.wali_relation = QtWidgets.QLineEdit()
        self.wali_address = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.wali_address)

        # witness 1
        self.witness1_name = QtWidgets.QLineEdit()
        self.witness1_father = QtWidgets.QLineEdit()
        self.witness1_age = QtWidgets.QSpinBox(); self.witness1_age.setRange(0, 120)
        self.witness1_address = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.witness1_address)

        # witness 2
        self.witness2_name = QtWidgets.QLineEdit()
        self.witness2_father = QtWidgets.QLineEdit()
        self.witness2_age = QtWidgets.QSpinBox(); self.witness2_age.setRange(0, 120)
        self.witness2_address = QtWidgets.QPlainTextEdit(); self._promote_as_address(self.witness2_address)

        # mahr & qazi
        self.mahr_words = QtWidgets.QLineEdit()
        self.mahr_figure = QtWidgets.QLineEdit()
        self.qazi_name = QtWidgets.QLineEdit()
        # self.qazi_certificate = QtWidgets.QLineEdit()

        self.mahr_figure.textChanged.connect(self._auto_fill_mahr_words)

        # ---------- Registry for data I/O ----------
        self._fields = [
            ("serial_no", "Serial No.", self.serial_no),
            ("reg_no", "Reg. No.", self.reg_no),
            ("masjid_name", "Masjid Name", self.masjid_name),

            ("hijri_date", "Hijri Date (text)", self.hijri_date),
            ("eng_date", "English Date", self.eng_date),
            ("nikah_time", "Time", self.nikah_time),
            ("place_of_nikah", "Place of Nikah", self.place_of_nikah),

            ("groom_name", "Groom Name", self.groom_name),
            ("groom_father", "Groom Father", self.groom_father),
            ("groom_age", "Groom Age", self.groom_age),
            # ("groom_status", "Groom Marital Status", self.groom_status),
            ("groom_address", "Groom Address", self.groom_address),

            ("bride_name", "Bride Name", self.bride_name),
            ("bride_father", "Bride Father", self.bride_father),
            ("bride_age", "Bride Age", self.bride_age),
            # ("bride_status", "Bride Marital Status", self.bride_status),
            ("bride_address", "Bride Address", self.bride_address),

            ("wali_name", "Wali/Wakil Name", self.wali_name),
            ("wali_age", "Wali Age", self.wali_age),
            ("wali_relation", "Wali Relation", self.wali_relation),
            ("wali_address", "Wali Address", self.wali_address),

            ("witness1_name", "Witness 1 Name", self.witness1_name),
            ("witness1_father", "Witness 1 Father", self.witness1_father),
            ("witness1_age", "Witness 1 Age", self.witness1_age),
            ("witness1_address", "Witness 1 Address", self.witness1_address),

            ("witness2_name", "Witness 2 Name", self.witness2_name),
            ("witness2_father", "Witness 2 Father", self.witness2_father),
            ("witness2_age", "Witness 2 Age", self.witness2_age),
            ("witness2_address", "Witness 2 Address", self.witness2_address),

            ("mahr_words", "Mahr (Words)", self.mahr_words),
            ("mahr_figure", "Mahr (Figure)", self.mahr_figure),
            ("qazi_name", "Qazi Name", self.qazi_name),
            # ("qazi_certificate", "Qazi Certificate/Seal Text", self.qazi_certificate),
        ]

        # ---------- Build two-column layout ----------
        # LEFT column: Header, Event, Groom, Bride
        g = self._section("", side="left")
        self._add_row3(g, [("Serial No.", self.serial_no),
                           ("Reg. No.", self.reg_no),
                           ("Masjid Name", self.masjid_name)])

        g = self._section("", side="left")
        self._add_row3(g, [("Hijri Date (text)", self.hijri_date),
                           ("English Date", self.eng_date),
                           ("Time", self.nikah_time)])
        self._add_fullrow(g, "Place of Nikah", self.place_of_nikah)

        g = self._section("", side="left")
        self._add_row3(g, [("Groom Name", self.groom_name),
                           ("Groom Father", self.groom_father),
                           ("Groom Age", self.groom_age)])
        # self._add_row3(g, [("Groom Marital Status", self.groom_status)])
        self._add_fullrow(g, "Groom Address", self.groom_address)

        g = self._section("", side="left")
        self._add_row3(g, [("Bride Name", self.bride_name),
                           ("Bride Father", self.bride_father),
                           ("Bride Age", self.bride_age)])
        # self._add_row3(g, [("Bride Marital Status", self.bride_status)])
        self._add_fullrow(g, "Bride Address", self.bride_address)

        # RIGHT column: Wali/Wakil, Witness 1, Witness 2, Mahr & Qazi
        g = self._section("", side="right")
        self._add_row3(g, [("Wali/Wakil Name", self.wali_name),
                           ("Wali Relation", self.wali_relation),
                           ("Wali Age", self.wali_age)])
        self._add_fullrow(g, "Wali Address", self.wali_address)

        g = self._section("Witness 1", side="right")
        self._add_row3(g, [("Name", self.witness1_name),
                           ("Father", self.witness1_father),
                           ("Age", self.witness1_age)])
        self._add_fullrow(g, "Address", self.witness1_address)

        g = self._section("Witness 2", side="right")
        self._add_row3(g, [("Name", self.witness2_name),
                           ("Father", self.witness2_father),
                           ("Age", self.witness2_age)])
        self._add_fullrow(g, "Address", self.witness2_address)

        g = self._section("", side="right")
        self._add_row3(g, [("Mahr (Words)", self.mahr_words),
                           ("Mahr (Figure)", self.mahr_figure),
                           ("Qazi Name", self.qazi_name)])

        # Pack columns and finish
        self.left_vbox.addStretch(1)
        self.right_vbox.addStretch(1)
        self.vbox.addLayout(cols_hbox)

    # ---------- helpers to build grid rows ----------
    def _section(self, title: str, side: str = "left") -> QtWidgets.QGridLayout:
        """
        Create a titled QGroupBox with a 6-column grid and add it to left/right column.
        Columns: (label, field) x 3
        """
        box = QtWidgets.QGroupBox(title)
        grid = QtWidgets.QGridLayout(box)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        # 6 columns: label1, field1, label2, field2, label3, field3
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 0)
        grid.setColumnStretch(3, 3)
        grid.setColumnStretch(4, 0)
        grid.setColumnStretch(5, 3)

        # per-section row counter
        box._row = 0
        box._grid = grid

        # attach to target column
        if side == "right":
            self.right_vbox.addWidget(box)
        else:
            self.left_vbox.addWidget(box)

        return grid

    def _add_row3(self, grid: QtWidgets.QGridLayout, pairs):
        """
        Add up to 3 (label, widget) pairs on one row.
        """
        row = grid.parentWidget()._row
        col = 0
        for label, widget in pairs[:3]:
            lbl = QtWidgets.QLabel(label + ":")
            lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            grid.addWidget(lbl, row, col)
            grid.addWidget(widget, row, col + 1)
            col += 2
        grid.parentWidget()._row += 1

    def _add_fullrow(self, grid: QtWidgets.QGridLayout, label: str, widget: QtWidgets.QWidget):
        """
        Full-width row within the column (label + widget spans remaining cols).
        """
        row = grid.parentWidget()._row
        lbl = QtWidgets.QLabel(label + ":")
        lbl.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        grid.addWidget(lbl, row, 0)
        grid.addWidget(widget, row, 1, 1, 5)  # span across 5 columns (1..5)
        grid.parentWidget()._row += 1

    def _promote_as_address(self, w: QtWidgets.QPlainTextEdit):
        w.setFixedHeight(48)
        w.setTabChangesFocus(True)

    def _auto_fill_mahr_words(self, text: str):
        words = amount_to_words_indian(text)
        self.mahr_words.setText(words)

    # ---------- Public helpers ----------
    def get_data(self) -> dict:
        d = {}
        for key, _, w in self._fields:
            if isinstance(w, QtWidgets.QLineEdit):
                d[key] = w.text().strip()
            elif isinstance(w, QtWidgets.QPlainTextEdit):
                d[key] = w.toPlainText().strip()
            elif isinstance(w, QtWidgets.QSpinBox):
                d[key] = w.value()
            elif isinstance(w, QtWidgets.QComboBox):
                d[key] = w.currentText()
            elif isinstance(w, QtWidgets.QDateEdit):
                d[key] = w.date().toString("yyyy-MM-dd")
            elif isinstance(w, QtWidgets.QTimeEdit):
                d[key] = w.time().toString("HH:mm")
        return d

    def set_data(self, data: dict):
        for key, _, w in self._fields:
            val = data.get(key, "")
            if isinstance(w, QtWidgets.QLineEdit):
                w.setText("" if val is None else str(val))
            elif isinstance(w, QtWidgets.QPlainTextEdit):
                w.setPlainText("" if val is None else str(val))
            elif isinstance(w, QtWidgets.QSpinBox):
                try:
                    w.setValue(int(val) if val not in (None, "") else 0)
                except Exception:
                    w.setValue(0)
            elif isinstance(w, QtWidgets.QComboBox):
                idx = w.findText("" if val is None else str(val))
                w.setCurrentIndex(idx if idx >= 0 else 0)
            elif isinstance(w, QtWidgets.QDateEdit):
                d = QtCore.QDate.fromString(str(val), "yyyy-MM-dd")
                if not d.isValid():
                    d = QtCore.QDate.currentDate()
                w.setDate(d)
            elif isinstance(w, QtWidgets.QTimeEdit):
                t = QtCore.QTime.fromString(str(val), "HH:mm")
                if not t.isValid():
                    t = QtCore.QTime.currentTime()
                w.setTime(t)

    def clear(self):
        for _, _, w in self._fields:
            if isinstance(w, QtWidgets.QLineEdit):
                w.clear()
            elif isinstance(w, QtWidgets.QPlainTextEdit):
                w.clear()
            elif isinstance(w, QtWidgets.QSpinBox):
                w.setValue(0)
            elif isinstance(w, QtWidgets.QComboBox):
                w.setCurrentIndex(0)
            elif isinstance(w, QtWidgets.QDateEdit):
                w.setDate(QtCore.QDate.currentDate())
            elif isinstance(w, QtWidgets.QTimeEdit):
                w.setTime(QtCore.QTime.currentTime())
        # self.groom_age.setValue(25)
        # self.bride_age.setValue(23)

# ---------- Amount-to-words (Indian numbering system) ----------
NUMS_1_TO_19 = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen"
]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

def _words_below_100(n: int) -> str:
    if n < 20:
        return NUMS_1_TO_19[n]
    return (TENS[n // 10] + (" " + NUMS_1_TO_19[n % 10] if n % 10 != 0 else "")).strip()

def _words_below_1000(n: int) -> str:
    if n == 0:
        return ""
    h, r = divmod(n, 100)
    parts = []
    if h:
        parts.append(NUMS_1_TO_19[h] + " Hundred")
    if r:
        parts.append(_words_below_100(r))
    return " ".join(parts).strip()

def _rupees_to_words_indian(n: int) -> str:
    """Indian grouping: Crore, Lakh, Thousand, Hundred."""
    if n == 0:
        return "Zero Rupees"
    parts = []
    crore, n = divmod(n, 10_000_000)
    lakh,  n = divmod(n, 100_000)
    thousand, n = divmod(n, 1000)
    hundred_block = n  # 0..999

    if crore:
        parts.append(_words_below_100(crore) + " Crore")
    if lakh:
        parts.append(_words_below_100(lakh) + " Lakh")
    if thousand:
        parts.append(_words_below_100(thousand) + " Thousand")
    if hundred_block:
        parts.append(_words_below_1000(hundred_block))

    return (" ".join(parts).strip() + " Rupees").strip()

def amount_to_words_indian(s: str) -> str:
    """
    Convert figure like "125000.50" -> "One Lakh Twenty Five Thousand Rupees and Fifty Paise Only"
    Handles commas and currency symbols; empty or invalid -> "".
    """
    if not s or not str(s).strip():
        return ""
    # keep digits and a single dot for paise
    cleaned = re.sub(r"[^0-9.]", "", str(s))
    if cleaned.count(".") > 1:
        # too many dots -> invalid
        return ""

    rupees_part, paise_part = cleaned, ""
    if "." in cleaned:
        rupees_part, paise_part = cleaned.split(".", 1)
        paise_part = (paise_part + "00")[:2]  # at most 2 digits

    if rupees_part == "":
        rupees = 0
    else:
        try:
            rupees = int(rupees_part)
        except ValueError:
            return ""

    words = _rupees_to_words_indian(rupees)

    # add paise if present and non-zero
    if paise_part and paise_part != "00":
        try:
            p = int(paise_part)
        except ValueError:
            p = 0
        if p:
            paise_words = _words_below_100(p)
            if words:
                words = f"{words} and {paise_words} Paise"
            else:
                words = f"{paise_words} Paise"

    if not words:
        return ""
    # finalize
    if not words.lower().endswith("only"):
        words = words + " Only"
    return words
