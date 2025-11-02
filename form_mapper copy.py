import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsView, 
                          QGraphicsScene, QGraphicsPixmapItem, 
                          QGraphicsTextItem, QPushButton, QVBoxLayout, 
                          QHBoxLayout, QWidget, QFileDialog, QInputDialog,
                          QListWidget, QMessageBox, QLabel, QSpinBox,
                          QTextEdit, QGroupBox, QCheckBox)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QTextCursor
from PyQt5.QtCore import Qt, QPointF, pyqtSignal

class DraggableTextItem(QGraphicsTextItem):
 def __init__(self, text, text_id, parent_editor):
     super().__init__(text)
     self.text_id = text_id
     self.parent_editor = parent_editor
     self.setFlag(QGraphicsTextItem.ItemIsMovable)
     self.setFlag(QGraphicsTextItem.ItemIsSelectable)
     self.setTextInteractionFlags(Qt.NoTextInteraction)
     self.setDefaultTextColor(QColor(0, 0, 255))
     font = QFont("Arial", 12)
     self.setFont(font)
     
 def mousePressEvent(self, event):
     self.setDefaultTextColor(QColor(255, 0, 0))
     self.parent_editor.update_property_panel(self)
     super().mousePressEvent(event)
     
 def mouseReleaseEvent(self, event):
     self.setDefaultTextColor(QColor(0, 0, 255))
     super().mouseReleaseEvent(event)

class ImageTextEditor(QMainWindow):
 def __init__(self):
     super().__init__()
     self.setWindowTitle("Image Text Position Editor")
     self.setGeometry(100, 100, 1400, 800)
     
     self.text_items = {}
     self.image_path = None
     self.dpi = 96
     self.current_selected_item = None
     
     self.init_ui()
     
 def init_ui(self):
     main_widget = QWidget()
     self.setCentralWidget(main_widget)
     main_layout = QHBoxLayout(main_widget)
     
     # Left side - Graphics View
     self.scene = QGraphicsScene()
     self.view = QGraphicsView(self.scene)
     self.view.setRenderHint(QPainter.Antialiasing)
     main_layout.addWidget(self.view, 3)
     
     # Right side - Controls
     control_layout = QVBoxLayout()
     
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
     
     # Buttons
     btn_load_image = QPushButton("Load Image")
     btn_load_image.clicked.connect(self.load_image)
     control_layout.addWidget(btn_load_image)
     
     btn_load_sample_data = QPushButton("Load Sample Data (JSON)")
     btn_load_sample_data.clicked.connect(self.load_sample_data)
     btn_load_sample_data.setStyleSheet("background-color: #4CAF50; color: white;")
     control_layout.addWidget(btn_load_sample_data)
     
     # NEW BUTTON - Load with coordinates and data
     btn_load_with_coords = QPushButton("Load Coords + Data")
     btn_load_with_coords.clicked.connect(self.load_with_coordinates_and_data)
     btn_load_with_coords.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
     control_layout.addWidget(btn_load_with_coords)
     
     btn_add_text = QPushButton("Add Text Field")
     btn_add_text.clicked.connect(self.add_text_field)
     control_layout.addWidget(btn_add_text)
     
     btn_remove_text = QPushButton("Remove Selected")
     btn_remove_text.clicked.connect(self.remove_selected_text)
     control_layout.addWidget(btn_remove_text)
     
     btn_save_coords = QPushButton("Save Coordinates")
     btn_save_coords.clicked.connect(self.save_coordinates)
     control_layout.addWidget(btn_save_coords)
     
     btn_load_coords = QPushButton("Load Coordinates")
     btn_load_coords.clicked.connect(self.load_coordinates)
     control_layout.addWidget(btn_load_coords)
     
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
     self.font_size_spinbox.setValue(12)
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
     
 def load_image(self):
     file_path, _ = QFileDialog.getOpenFileName(
         self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
     )
     
     if file_path:
         self.image_path = file_path
         pixmap = QPixmap(file_path)
         self.scene.clear()
         self.text_items.clear()
         self.text_list.clear()
         
         pixmap_item = QGraphicsPixmapItem(pixmap)
         self.scene.addItem(pixmap_item)
         self.scene.setSceneRect(pixmap_item.boundingRect())
 
 def load_sample_data(self):
     if not self.image_path:
         QMessageBox.warning(self, "Warning", "Please load an image first!")
         return
     
     file_path, _ = QFileDialog.getOpenFileName(
         self, "Load Sample Data", "", "JSON Files (*.json)"
     )
     
     if file_path:
         with open(file_path, 'r') as f:
             sample_data = json.load(f)
         
         for item in list(self.text_items.values()):
             self.scene.removeItem(item)
         self.text_items.clear()
         self.text_list.clear()
         
         for text_id, text_value in sample_data.items():
             text_item = DraggableTextItem(str(text_value), text_id, self)
             text_item.setPos(50, 50 + len(self.text_items) * 30)
             self.scene.addItem(text_item)
             self.text_items[text_id] = text_item
             self.text_list.addItem(text_id)
         
         QMessageBox.information(self, "Success", 
             f"Loaded {len(sample_data)} fields from sample data!")
 
 # NEW METHOD - Load coordinates and apply data
 def load_with_coordinates_and_data(self):
     """Load coordinates JSON and data JSON, merge them and display"""
     if not self.image_path:
         QMessageBox.warning(self, "Warning", "Please load an image first!")
         return
     
     # Load coordinates JSON
     coords_path, _ = QFileDialog.getOpenFileName(
         self, "Select Coordinates JSON", "", "JSON Files (*.json)"
     )
     
     if not coords_path:
         return
     
     # Load data JSON
     data_path, _ = QFileDialog.getOpenFileName(
         self, "Select Data JSON", "", "JSON Files (*.json)"
     )
     
     if not data_path:
         return
     
     # Read both files
     with open(coords_path, 'r') as f:
         coords_data = json.load(f)
     
     with open(data_path, 'r') as f:
         text_data = json.load(f)
     
     # Apply data with coordinates
     self.apply_data_with_coordinates(coords_data, text_data)
 
 def apply_data_with_coordinates(self, coords_data, text_data):
     """Apply text data using saved coordinates"""
     # Load DPI from coords
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
         # Get text from data dictionary (if exists, otherwise use saved text)
         text_content = str(text_data.get(field_id, field_info.get("text", "")))
         
         # Create text item
         text_item = DraggableTextItem(text_content, field_id, self)
         
         # Set font size
         font = text_item.font()
         font.setPointSize(field_info.get("font_size", 12))
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
     
     QMessageBox.information(self, "Success", 
         f"Loaded {len(fields)} fields with coordinates and data!")
 
 # BONUS: Method to load data programmatically (can be called from code)
 def load_data_dict(self, coords_json_path, data_dict):
     """
     Programmatically load coordinates and data
     
     Args:
         coords_json_path: Path to coordinates JSON
         data_dict: Dictionary with data {"name": "John", "address": "123 St", ...}
     """
     with open(coords_json_path, 'r') as f:
         coords_data = json.load(f)
     
     self.apply_data_with_coordinates(coords_data, data_dict)
         
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
     if not self.text_items:
         QMessageBox.warning(self, "Warning", "No text fields to save!")
         return
         
     file_path, _ = QFileDialog.getSaveFileName(
         self, "Save Coordinates", "", "JSON Files (*.json)"
     )
     
     if file_path:
         coordinates = {}
         for text_id, item in self.text_items.items():
             print(item.toPlainText())
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
         
         with open(file_path, 'w') as f:
             json.dump(data, f, indent=4)
             
         QMessageBox.information(self, "Success", 
             f"Coordinates saved successfully!\nDPI: {self.dpi}\nUnit: millimeters")
         
 def load_coordinates(self):
     if not self.image_path:
         QMessageBox.warning(self, "Warning", "Please load an image first!")
         return
         
    #  file_path, _ = QFileDialog.getOpenFileName(
    #      self, "Load Coordinates", "", "JSON Files (*.json)"
    #  )
     file_path = 'data/test.json'
     
     if file_path:
         with open(file_path, 'r') as f:
             data = json.load(f)
         
         saved_dpi = data.get("dpi", 96)
         self.dpi_spinbox.setValue(saved_dpi)
         
         for item in list(self.text_items.values()):
             self.scene.removeItem(item)
         self.text_items.clear()
         self.text_list.clear()
         
         fields = data.get("fields", {})
         for text_id, field_data in fields.items():
             text_item = DraggableTextItem(field_data["text"], text_id, self)
             
             font = text_item.font()
             font.setPointSize(field_data.get("font_size", 12))
             text_item.setFont(font)
             
             text_width = field_data.get("text_width", -1)
             text_item.setTextWidth(text_width)
             
             x_pixels = self.mm_to_pixels(field_data["x_mm"])
             y_pixels = self.mm_to_pixels(field_data["y_mm"])
             
             text_item.setPos(QPointF(x_pixels, y_pixels))
             self.scene.addItem(text_item)
             self.text_items[text_id] = text_item
             self.text_list.addItem(text_id)
             
         QMessageBox.information(self, "Success", 
             f"Coordinates loaded successfully!\nOriginal DPI: {saved_dpi}\nCurrent DPI: {self.dpi}")

if __name__ == "__main__":
 app = QApplication(sys.argv)
 window = ImageTextEditor()
 window.show()
 
 # EXAMPLE: Load programmatically with dictionary
 # Uncomment and modify paths to use:
 window.image_path = "images/nn_preprint_blank.png"
 pixmap = QPixmap("images/nn_preprint_blank.png")
 pixmap_item = QGraphicsPixmapItem(pixmap)
 window.scene.addItem(pixmap_item)
 window.scene.setSceneRect(pixmap_item.boundingRect())
 my_data = {
  "SrNo": "2025-00098",
  "HijriDate": "1447-09-25",
  "EnglishDate": "27th October 2025",
  "Time": "11:45 AM",
  "PlaceOfNikah": "Masjid Ahle Hadees, Kurla, Fitwalla bldg., Pipe Road, M.P. Marg, Kurla West, Mumbai 400070",

  "Bridegroom": "Mohammed Abdullah bin Abdul Kareem Al-Farouqi,\n32 years, Flat No. 404, Green Meadows Apartment,\nNear Kurla Railway Station, Mumbai-400070.",

  "Bride": "Ayesha Fatima bint Ahmed Khan, 28 years, \nHouse No. 123, Pearl Residency, 5th Cross Road, \nBandra West, Mumbai-400050",

  "Wali": "\t\tAhmed Khan s/o Late Abdul Rahman Khan, 56 years,\nHouse No. 123, Pearl Residency, 5th Cross Road, Bandra West, Mumbai-400050",

  "Witness1": "Yusuf Abdul Majid Shaikh, 40 years, House No. 12,\nNoor Apartment, M.T. Marg, Kurla (West), Mumbai-400070",

  "Witness2": "Imran Abdul Hafeez Qureshi, 35 years, 45/7,\nSunshine Tower, Byculla East, Mumbai-400027",

  "Mahr": "One Lakh Twenty-Five Thousand Indian Rupees only",

  "QaziNameSeal": "Qazi Abdul Rahman\nAl-Hindi",

  "mahr_in_figures": "11,25,000.00",
  "bride_name_only": "Ayesha Fatima d/o Ahmed Khan",
  "groom_name_only": "Mohammed Abdullah s/o \nAbdul Kareem Al-Farouqi",
  "mahr_in_words": "One Lakh Twenty-Five\nThousand Indian Rupees only"
}

 
 window.load_data_dict("coordinates.json", my_data)
 
 sys.exit(app.exec_())