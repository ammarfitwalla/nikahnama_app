# ui/records_table.py
from PyQt5 import QtCore, QtWidgets

class RecordsTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.setMinimumHeight(200)

    def load_records(self, rows: list, columns: list, headers: list):
        self.clear()
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(headers)
        self.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, col in enumerate(columns):
                val = row.get(col, "")
                item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
                self.setItem(r, c, item)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def selected_id(self):
        sel = self.selectionModel().selectedRows()
        if not sel:
            return None
        row = sel[0].row()
        item = self.item(row, 0)  # column 0 is id
        return int(item.text()) if item else None

    def row_dict(self, row_index: int, columns: list) -> dict:
        d = {}
        for c, name in enumerate(columns):
            it = self.item(row_index, c)
            d[name] = it.text() if it else ""
        return d
