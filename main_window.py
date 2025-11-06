# main_window.py
from PyQt5 import QtWidgets, QtPrintSupport, QtGui, QtCore
from PyQt5.QtCore import QSettings
from constants import DB_COLUMNS, HEADERS, REQUIRED_FIELDS
from database import insert_record, update_record, delete_record, fetch_all
from ui.nikah_form import NikahForm
from ui.records_table import RecordsTable
from print_layout import draw_certificate
from field_mapper import map_form_to_print
import os

class PrintOptionsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Print Options")
        self.setModal(True)
        self.settings = QtCore.QSettings()

        form = QtWidgets.QFormLayout(self)

        self.chk_bg = QtWidgets.QCheckBox("Show template background for calibration")
        self.chk_grid = QtWidgets.QCheckBox("Show 10mm grid")
        self.ed_template = QtWidgets.QLineEdit(os.path.abspath("data/nn_preprint_blank.png"))
        btn_browse = QtWidgets.QPushButton("Browse…")
        def browse():
            p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select template image", "", "Images (*.png *.jpg *.jpeg)")
            if p:
                self.ed_template.setText(p)
        btn_browse.clicked.connect(browse)

        self.off_x = QtWidgets.QDoubleSpinBox(); self.off_x.setRange(-50, 50); self.off_x.setDecimals(1); self.off_x.setSuffix(" mm")
        self.off_y = QtWidgets.QDoubleSpinBox(); self.off_y.setRange(-50, 50); self.off_y.setDecimals(1); self.off_y.setSuffix(" mm")

        # restore last offsets
        self.off_x.setValue(float(self.settings.value("print/offset_x_mm", 0.0)))
        self.off_y.setValue(float(self.settings.value("print/offset_y_mm", 0.0)))
        self.chk_bg.setChecked(bool(int(self.settings.value("print/show_template", 0))))
        self.chk_grid.setChecked(bool(int(self.settings.value("print/show_grid", 0))))

        # layout
        form.addRow(self.chk_bg)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.ed_template, 1); row.addWidget(btn_browse)
        form.addRow("Template image:", row)
        form.addRow(self.chk_grid)
        form.addRow("Offset X:", self.off_x)
        form.addRow("Offset Y:", self.off_y)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        form.addRow(btns)

    def values(self):
        return dict(
            show_template=self.chk_bg.isChecked(),
            template_path=self.ed_template.text().strip(),
            show_grid=self.chk_grid.isChecked(),
            offset_x=float(self.off_x.value()),
            offset_y=float(self.off_y.value()),
        )

    def accept(self):
        v = self.values()
        self.settings.setValue("print/offset_x_mm", v["offset_x"])
        self.settings.setValue("print/offset_y_mm", v["offset_y"])
        self.settings.setValue("print/show_template", int(v["show_template"]))
        self.settings.setValue("print/show_grid", int(v["show_grid"]))
        super().accept()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        QtCore.QCoreApplication.setOrganizationName("MyCompany")
        QtCore.QCoreApplication.setApplicationName("NikahnamaAdmin")

        self.setWindowTitle("Nikahnama Admin (PyQt5)")
        self.resize(1400, 900)
        self.current_id = None

        self.settings = QtCore.QSettings()
        self._build()
        self._restore_settings()
        self.reload_table()

    def _build(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        vbox = QtWidgets.QVBoxLayout(central)
        vbox.setContentsMargins(8, 8, 8, 8)

        # form (scrollable)
        self.form = NikahForm()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.form)

        # buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setContentsMargins(8, 6, 8, 6)
        btn_row.setSpacing(8)
        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_clear = QtWidgets.QPushButton("Clear")
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_print = QtWidgets.QPushButton("Print")
        
        self.btn_delete.setDisabled(True)
        self.btn_clear.setDisabled(True)
        self.btn_print.setDisabled(True)
        
        # search beside buttons
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("Search…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setMinimumWidth(300)

        btn_row.addWidget(QtWidgets.QLabel("Search:"))
        btn_row.addWidget(self.search_edit)

        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_print)

        btn_widget = QtWidgets.QWidget()
        btn_widget.setLayout(btn_row)
        btn_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        btn_widget.setMaximumHeight(self.btn_save.sizeHint().height() + 18)

        # table
        self.table = RecordsTable()
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultSectionSize(140)
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)

        # splitter
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.addWidget(scroll)
        self.splitter.addWidget(btn_widget)
        self.splitter.addWidget(self.table)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStretchFactor(2, 4)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setCollapsible(2, False)

        if not self.settings.value("splitter/sizes"):
            self.splitter.setSizes([380, 12, 520])

        vbox.addWidget(self.splitter)

        # status bar
        self.status = self.statusBar()
        self.status.showMessage("Ready")

        # signals
        self.btn_save.clicked.connect(self.save_clicked)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_delete.clicked.connect(self.delete_clicked)
        self.btn_print.clicked.connect(self.print_clicked)
        self.table.itemSelectionChanged.connect(self.table_selection_changed)
        self.search_edit.textChanged.connect(self.on_search_text_changed)

    def _restore_settings(self):
        geo = self.settings.value("window/geometry", type=QtCore.QByteArray)
        state = self.settings.value("window/state", type=QtCore.QByteArray)
        if geo:
            self.restoreGeometry(geo)
        if state:
            self.restoreState(state)

        sizes = self.settings.value("splitter/sizes")
        if sizes:
            try:
                self.splitter.setSizes([int(s) for s in sizes])
            except Exception:
                pass

        hdr_state = self.settings.value("table/headerState", type=QtCore.QByteArray)
        if hdr_state:
            self.table.horizontalHeader().restoreState(hdr_state)

    def closeEvent(self, event):
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
        self.settings.setValue("splitter/sizes", self.splitter.sizes())
        self.settings.setValue("table/headerState", self.table.horizontalHeader().saveState())
        super().closeEvent(event)

    def reload_table(self):
        rows = fetch_all()
        self.table.load_records(rows, DB_COLUMNS, HEADERS)
        self.apply_filter()

    def select_row_by_id(self, rec_id: int):
        for r in range(self.table.rowCount()):
            it = self.table.item(r, 0)
            if it and it.text() == str(rec_id):
                self.table.selectRow(r)
                return

    def table_selection_changed(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return
        row = sel[0].row()
        data = self.table.row_dict(row, DB_COLUMNS)
        self.current_id = int(data.get("id", "0")) or None
        self.form.set_data(data)
        self.status.showMessage(f"Loaded record #{self.current_id} into form.")
        self.btn_print.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_clear.setEnabled(True)

    def clear_form(self):
        self.current_id = None
        self.form.clear()
        self.table.clearSelection()
        self.status.showMessage("Form cleared.")
        self.btn_print.setDisabled(True)
        self.btn_delete.setDisabled(True)
        self.btn_clear.setDisabled(True)

    def save_clicked(self):
        data = self.form.get_data()
        missing = [k for k in REQUIRED_FIELDS if not str(data.get(k, "")).strip()]
        if missing:
            QtWidgets.QMessageBox.warning(self, "Missing", f"Please fill required fields: {', '.join(missing)}")
            return
        if self.current_id is None:
            rec_id = insert_record(data)
            self.status.showMessage(f"Inserted record #{rec_id}.")
            self.reload_table()
            self.current_id = rec_id
            self.select_row_by_id(rec_id)
        else:
            update_record(self.current_id, data)
            self.status.showMessage(f"Updated record #{self.current_id}.")
            self.reload_table()
            self.select_row_by_id(self.current_id)

    def delete_clicked(self):
        rec_id = self.table.selected_id()
        if rec_id is None:
            QtWidgets.QMessageBox.information(self, "Delete", "Please select a row to delete.")
            return
        ok = QtWidgets.QMessageBox.question(self, "Delete", f"Delete record #{rec_id}?",
                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ok != QtWidgets.QMessageBox.Yes:
            return
        delete_record(rec_id)
        self.current_id = None
        self.form.clear()
        self.reload_table()
        self.status.showMessage(f"Deleted record #{rec_id}.")

    def print_clicked(self):
        """Open form mapper for layout configuration, then print"""
        data = self.form.get_data()
        print('data in print_clicked')
        print(data)
        
        # Check if we have data to print
        if not data or not any(data.values()):
            QtWidgets.QMessageBox.warning(self, "No Data", 
                "Please load or enter certificate data before printing.")
            return
        
        # Map form data to print field names
        print_data = map_form_to_print(data)
        
        # Get template path from settings or use default
        template_path = self.settings.value("print/template_path", "data/nn_preprint_blank.png")
        if not os.path.exists(template_path):
            template_path = "data/nn_preprint_blank.png"
        
        # Open form mapper with current data
        try:
            from form_mapper import ImageTextEditor
            print('print_data', print_data)
            
            self.form_mapper = ImageTextEditor(
                parent=self,
                initial_data=print_data,
                template_path=template_path,
                coords_path="coordinates.json"
            )
            
            # Connect signal to know when printing is done
            self.form_mapper.print_completed.connect(self.on_print_completed)
            
            # Show the form mapper
            self.form_mapper.show()
            self.status.showMessage("Configure text positions, then click 'Save & Print'")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", 
                f"Failed to open layout editor: {str(e)}")

    def on_print_completed(self):
        """Called when printing is completed from form mapper"""
        self.status.showMessage("Certificate printed successfully!")

    def on_search_text_changed(self, text: str):
        self.current_filter_text = text.strip().lower()
        self.apply_filter()

    def apply_filter(self):
        """Show only rows that contain the search text in ANY column"""
        text = getattr(self, "current_filter_text", "")
        if self.table.rowCount() == 0:
            return

        if not text:
            for r in range(self.table.rowCount()):
                self.table.setRowHidden(r, False)
            return

        for r in range(self.table.rowCount()):
            match = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(r, not match)