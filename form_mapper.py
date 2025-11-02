import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                       QGraphicsScene, QGraphicsPixmapItem, 
                       QGraphicsTextItem, QPushButton, QVBoxLayout, 
                       QHBoxLayout, QWidget, QFileDialog, QInputDialog,
                       QListWidget, QMessageBox, QLabel, QSpinBox,
                       QTextEdit, QGroupBox)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5 import QtPrintSupport, QtGui

class DraggableTextItem(QGraphicsTextItem):
 def __init__(self, text, text_id, parent_editor):
     super().__init__(text)
     self.text_id = text_id
     self.parent_editor = parent_editor
     self.setFlag(QGraphicsTextItem.ItemIsMovable)
     self.setFlag(QGraphicsTextItem.ItemIsSelectable)
     self.setTextInteractionFlags(Qt.NoTextInteraction)
     self.setDefaultTextColor(QColor(255, 0, 0))  # Red for better visibility
     font = QFont("Arial", 14, QFont.Bold)
     self.setFont(font)
     self.setZValue(100)  # Ensure text is above image
     
 def mousePressEvent(self, event):
     self.setDefaultTextColor(QColor(0, 255, 0))  # Green when selected
     self.parent_editor.update_property_panel(self)
     super().mousePressEvent(event)
     
 def mouseReleaseEvent(self, event):
     self.setDefaultTextColor(QColor(255, 0, 0))  # Back to red
     super().mouseReleaseEvent(event)

class ImageTextEditor(QMainWindow):
 print_completed = pyqtSignal()
 
 def __init__(self, parent=None, initial_data=None, template_path=None, coords_path=None):
     super().__init__(parent)
     self.setWindowTitle("Certificate Layout Editor - Position Text Fields")
     self.setGeometry(100, 100, 1400, 800)
     
     self.text_items = {}
     self.image_path = template_path or "images/nn_preprint_blank.png"
     self.coords_file = coords_path or "coordinates.json"
     print(coords_path)
     self.initial_data = initial_data or {}
     self.dpi = 96
     self.current_selected_item = None
     self.parent_window = parent
     
     # DEBUG INFO
     print(f"\n{'='*50}")
     print(f"🚀 INITIALIZING IMAGE TEXT EDITOR")
     print(f"{'='*50}")
     print(f"📊 Initial data: {self.initial_data}")
     print(f"🖼️ Template path: {self.image_path}")
     print(f"📍 Coords path: {self.coords_file}")
     print(f"✅ Image exists: {os.path.exists(self.image_path)}")
     print(f"✅ Coords exists: {os.path.exists(self.coords_file)}")
     print(f"{'='*50}\n")
     
     self.init_ui()
     
     # Auto-load image
     if self.image_path and os.path.exists(self.image_path):
         print("📸 Loading image...")
         self.load_image_from_path(self.image_path)
     else:
         print(f"⚠️ Image not found: {self.image_path}")
         
     # Try to load coordinates with data
     if self.initial_data:
         if os.path.exists(self.coords_file):
             print("📍 Loading with saved coordinates...")
             self.load_with_coordinates_and_data_auto()
         else:
             print("📝 No coordinates found, loading data in default positions...")
             self.load_initial_data_only()
     else:
         print("⚠️ No initial data provided!")
     
 def init_ui(self):
     main_widget = QWidget()
     self.setCentralWidget(main_widget)
     main_layout = QHBoxLayout(main_widget)
     
     # Left side - Graphics View
     self.scene = QGraphicsScene()
     self.view = QGraphicsView(self.scene)
     self.view.setRenderHint(QPainter.Antialiasing)
     self.view.setBackgroundBrush(QColor(240, 240, 240))  # Light gray background
     main_layout.addWidget(self.view, 3)
     
     # Right side - Controls
     control_layout = QVBoxLayout()
     
     # Instructions
     instructions = QLabel("📍 Instructions:\n"
                         "1. Drag RED text fields to position them\n"
                         "2. Click 'Save & Print' when done\n"
                         "3. Coordinates will be saved for future use")
     instructions.setStyleSheet("background-color: #E3F2FD; padding: 10px; border-radius: 5px;")
     instructions.setWordWrap(True)
     control_layout.addWidget(instructions)
     
     # DPI Setting
     dpi_layout = QHBoxLayout()
     dpi_label = QLabel("DPI:")
     self.dpi_spinbox = QSpinBox()
     self.dpi_spinbox.setRange(72, 600)
     self.dpi_spinbox.setValue(self.dpi)
     self.dpi_spinbox.valueChanged.connect(self.update_dpi)
     dpi_layout.addWidget(dpi_label)
     dpi_layout.addWidget(self.dpi_spinbox)
     control_layout.addLayout(dpi_layout)
     
     # Info label
     self.info_label = QLabel("Set DPI for your image\n(96 for screen, 300 for print)")
     self.info_label.setWordWrap(True)
     self.info_label.setStyleSheet("color: gray; font-size: 10px;")
     control_layout.addWidget(self.info_label)
     
     # Primary Action Button
     btn_save_and_print = QPushButton("🖨️ Print")
     btn_save_and_print.clicked.connect(self.save_and_print)
     btn_save_and_print.setStyleSheet("""
         QPushButton {
             background-color: #4CAF50; 
             color: white; 
             font-weight: bold;
             font-size: 14px;
             padding: 10px;
         }
         QPushButton:hover {
             background-color: #45a049;
         }
     """)
     control_layout.addWidget(btn_save_and_print)
     
     # Separator
     separator = QLabel("")
     separator.setStyleSheet("border-top: 2px solid #ddd; margin: 10px 0;")
     control_layout.addWidget(separator)
     
     # Optional buttons
     btn_load_image = QPushButton("Load Different Image")
     btn_load_image.clicked.connect(self.load_image)
     control_layout.addWidget(btn_load_image)
     
     btn_add_text = QPushButton("Add Text Field")
     btn_add_text.clicked.connect(self.add_text_field)
     control_layout.addWidget(btn_add_text)
     
     btn_remove_text = QPushButton("Remove Selected")
     btn_remove_text.clicked.connect(self.remove_selected_text)
     control_layout.addWidget(btn_remove_text)
     
     # Property Panel
     self.create_property_panel(control_layout)
     
     # List of text fields
     list_label = QLabel("Text Fields:")
     control_layout.addWidget(list_label)
     self.text_list = QListWidget()
     self.text_list.itemClicked.connect(self.select_text_from_list)
     control_layout.addWidget(self.text_list)
     
     control_layout.addStretch()
     
     main_layout.addLayout(control_layout, 1)
 
 def create_property_panel(self, parent_layout):
     property_group = QGroupBox("Edit Selected Text")
     property_layout = QVBoxLayout()
     
     self.prop_id_label = QLabel("ID: None")
     property_layout.addWidget(self.prop_id_label)
     
     # Font size
     font_layout = QHBoxLayout()
     font_label = QLabel("Font Size:")
     self.font_size_spinbox = QSpinBox()
     self.font_size_spinbox.setRange(6, 72)
     self.font_size_spinbox.setValue(14)
     self.font_size_spinbox.valueChanged.connect(self.update_font_size)
     font_layout.addWidget(font_label)
     font_layout.addWidget(self.font_size_spinbox)
     property_layout.addLayout(font_layout)
     
     # Width
     width_layout = QHBoxLayout()
     width_label = QLabel("Width (px):")
     self.width_spinbox = QSpinBox()
     self.width_spinbox.setRange(-1, 2000)
     self.width_spinbox.setValue(-1)
     self.width_spinbox.setSpecialValueText("Auto")
     self.width_spinbox.valueChanged.connect(self.update_text_width)
     width_layout.addWidget(width_label)
     width_layout.addWidget(self.width_spinbox)
     property_layout.addLayout(width_layout)
     
     # Text edit
     text_edit_label = QLabel("Text Content:")
     property_layout.addWidget(text_edit_label)
     self.text_edit = QTextEdit()
     self.text_edit.setMaximumHeight(100)
     self.text_edit.textChanged.connect(self.update_text_content)
     property_layout.addWidget(self.text_edit)
     
     property_group.setLayout(property_layout)
     parent_layout.addWidget(property_group)
 
 def update_property_panel(self, item):
     if not isinstance(item, DraggableTextItem):
         return
     
     self.current_selected_item = item
     
     self.text_edit.blockSignals(True)
     self.font_size_spinbox.blockSignals(True)
     self.width_spinbox.blockSignals(True)
     
     self.prop_id_label.setText(f"ID: {item.text_id}")
     self.text_edit.setPlainText(item.toPlainText())
     self.font_size_spinbox.setValue(item.font().pointSize())
     
     width = item.textWidth()
     if width == -1:
         self.width_spinbox.setValue(-1)
     else:
         self.width_spinbox.setValue(int(width))
     
     self.text_edit.blockSignals(False)
     self.font_size_spinbox.blockSignals(False)
     self.width_spinbox.blockSignals(False)
 
 def update_text_content(self):
     if self.current_selected_item:
         self.current_selected_item.setPlainText(self.text_edit.toPlainText())
 
 def update_font_size(self, size):
     if self.current_selected_item:
         font = self.current_selected_item.font()
         font.setPointSize(size)
         self.current_selected_item.setFont(font)
 
 def update_text_width(self, width):
     if self.current_selected_item:
         self.current_selected_item.setTextWidth(width)
 
 def select_text_from_list(self, item):
     text_id = item.text()
     if text_id in self.text_items:
         text_item = self.text_items[text_id]
         self.scene.clearSelection()
         text_item.setSelected(True)
         self.update_property_panel(text_item)
 
 def update_dpi(self, value):
     self.dpi = value
     
 def pixels_to_mm(self, pixels):
     return (pixels / self.dpi) * 25.4
 
 def mm_to_pixels(self, mm):
     return (mm * self.dpi) / 25.4
 
 def load_image_from_path(self, file_path):
     """Load image from a given path"""
     if os.path.exists(file_path):
         self.image_path = file_path
         pixmap = QPixmap(file_path)
         
         if pixmap.isNull():
             print(f"❌ Failed to load image: {file_path}")
             QMessageBox.critical(self, "Error", f"Failed to load image: {file_path}")
             return
         
         print(f"✅ Image loaded: {pixmap.width()}x{pixmap.height()}px")
         
         self.scene.clear()
         self.text_items.clear()
         self.text_list.clear()
         
         pixmap_item = QGraphicsPixmapItem(pixmap)
         pixmap_item.setZValue(-1)  # Put image behind text
         self.scene.addItem(pixmap_item)
         self.scene.setSceneRect(pixmap_item.boundingRect())
         
         print(f"📐 Scene rect: {self.scene.sceneRect()}")
     else:
         print(f"❌ Image file not found: {file_path}")
 
 def load_image(self):
     file_path, _ = QFileDialog.getOpenFileName(
         self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
     )
     
     if file_path:
         self.load_image_from_path(file_path)
 
 def load_with_coordinates_and_data_auto(self):
     """Auto-load coordinates and apply initial data"""
     if not os.path.exists(self.coords_file):
         print(f"⚠️ Coords file not found: {self.coords_file}")
         self.load_initial_data_only()
         return
     
     try:
         with open(self.coords_file, 'r') as f:
             coords_data = json.load(f)
         
         print(f"✅ Loaded coords: {len(coords_data.get('fields', {}))} fields")
         self.apply_data_with_coordinates(coords_data, self.initial_data)
         
     except Exception as e:
         print(f"❌ Error loading coordinates: {str(e)}")
         import traceback
         traceback.print_exc()
         QMessageBox.warning(self, "Warning", 
             f"Could not load coordinates: {str(e)}\nLoading data without coordinates.")
         self.load_initial_data_only()
 
 def load_initial_data_only(self):
     """Load initial data without coordinates"""
     if not self.initial_data:
         print("⚠️ No initial data provided!")
         QMessageBox.information(self, "No Data", 
             "No data to display. Use 'Add Text Field' to add fields manually.")
         return
     
     print(f"📝 Loading {len(self.initial_data)} fields without coordinates")
     
     for item in list(self.text_items.values()):
         self.scene.removeItem(item)
     self.text_items.clear()
     self.text_list.clear()
     
     y_offset = 50
     for field_id, text_value in self.initial_data.items():
         print(f"  Adding field: {field_id} = {text_value}")
         text_item = DraggableTextItem(str(text_value), field_id, self)
         text_item.setPos(50, y_offset)
         y_offset += 35
         self.scene.addItem(text_item)
         self.text_items[field_id] = text_item
         self.text_list.addItem(field_id)
     
     print(f"✅ Added {len(self.text_items)} text items to scene")
 
 def apply_data_with_coordinates(self, coords_data, text_data):
     """Apply text data using saved coordinates"""
     saved_dpi = coords_data.get("dpi", 96)
     self.dpi_spinbox.setValue(saved_dpi)
     
     # Clear existing
     for item in list(self.text_items.values()):
         self.scene.removeItem(item)
     self.text_items.clear()
     self.text_list.clear()
     
     # Load fields with coordinates
     fields = coords_data.get("fields", {})
     
     for field_id, field_info in fields.items():
         # Get text from data dictionary
        #  text_content = str(text_data.get(field_id, field_info.get("text", "")))
         text_content = str(text_data.get(field_id, ""))

         print(f"  Loading field: {field_id} = {text_content} at ({field_info['x_mm']}, {field_info['y_mm']}) mm")
         
         # Create text item
         text_item = DraggableTextItem(text_content, field_id, self)
         
         # Set font size
         font = text_item.font()
         font.setPointSize(field_info.get("font_size", 14))
         text_item.setFont(font)
         
         # Set text width
         text_width = field_info.get("text_width", -1)
         text_item.setTextWidth(text_width)
         
         # Convert mm to pixels
         x_pixels = self.mm_to_pixels(field_info["x_mm"])
         y_pixels = self.mm_to_pixels(field_info["y_mm"])
         
         text_item.setPos(QPointF(x_pixels, y_pixels))
         self.scene.addItem(text_item)
         self.text_items[field_id] = text_item
         self.text_list.addItem(field_id)
     
     print(f"✅ Loaded {len(self.text_items)} fields with coordinates")
 
 def add_text_field(self):
     if not self.image_path:
         QMessageBox.warning(self, "Warning", "Please load an image first!")
         return
         
     text_id, ok = QInputDialog.getText(
         self, "Add Text Field", "Enter field name/ID:"
     )
     
     if ok and text_id:
         if text_id in self.text_items:
             QMessageBox.warning(self, "Warning", "Field ID already exists!")
             return
             
         sample_text, ok = QInputDialog.getText(
             self, "Sample Text", f"Enter sample text for '{text_id}':"
         )
         
         if ok:
             text_item = DraggableTextItem(sample_text or text_id, text_id, self)
             text_item.setPos(50, 50)
             self.scene.addItem(text_item)
             self.text_items[text_id] = text_item
             self.text_list.addItem(text_id)
             
 def remove_selected_text(self):
     selected_items = self.scene.selectedItems()
     if selected_items:
         for item in selected_items:
             if isinstance(item, DraggableTextItem):
                 text_id = item.text_id
                 self.scene.removeItem(item)
                 del self.text_items[text_id]
                 
                 items = self.text_list.findItems(text_id, Qt.MatchExactly)
                 for list_item in items:
                     self.text_list.takeItem(self.text_list.row(list_item))
         
         self.current_selected_item = None
         self.prop_id_label.setText("ID: None")
         self.text_edit.clear()
 
 def save_coordinates(self):
     """Save coordinates to JSON file"""
     if not self.text_items:
         QMessageBox.warning(self, "Warning", "No text fields to save!")
         return False
     
     coordinates = {}
     for text_id, item in self.text_items.items():
         pos = item.pos()
         coordinates[text_id] = {
             "x_mm": round(self.pixels_to_mm(pos.x()), 2),
             "y_mm": round(self.pixels_to_mm(pos.y()), 2),
             "x_pixels": pos.x(),
             "y_pixels": pos.y(),
             "text": item.toPlainText(),
             "font_size": item.font().pointSize(),
             "text_width": item.textWidth()
         }
     
     data = {
         "image_path": self.image_path,
         "dpi": self.dpi,
         "unit": "millimeters",
         "fields": coordinates
     }
     
     try:
         with open(self.coords_file, 'w') as f:
             json.dump(data, f, indent=4)
         print(f"✅ Coordinates saved to: {self.coords_file}")
         return True
     except Exception as e:
         print(f"❌ Error saving coordinates: {str(e)}")
         QMessageBox.critical(self, "Error", f"Failed to save coordinates: {str(e)}")
         return False
 
 def save_and_print(self):
     """Save coordinates and trigger print"""
     self.save_coordinates()
    #      QMessageBox.information(self, "Success", 
        # f"Coordinates saved to {self.coords_file}\nProceeding to print...")
     self.trigger_print()
 

 def trigger_print(self):
        from PyQt5.QtWidgets import QDialog, QMessageBox
        """Trigger the print function"""
        try:
            from print_layout import draw_certificate_from_coords

            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setFullPage(True)
            printer.setPageSize(QtPrintSupport.QPrinter.A4)

            dlg = QtPrintSupport.QPrintDialog(printer, self)
            dlg.setWindowTitle("Select Printer")
            if dlg.exec_() != QDialog.Accepted:
                return

            painter = QtGui.QPainter(printer)
            try:
                draw_certificate_from_coords(
                    painter,
                    printer,
                    self.initial_data,
                    coords_file=self.coords_file,
                    show_template=True,
                    template_path=self.image_path,
                    debug_grid=False
                )
                QMessageBox.information(self, "Success", "Certificate printed successfully!")
                self.print_completed.emit()
                # self.close()
            finally:
                painter.end()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Print Error", f"Failed to print: {str(e)}")

