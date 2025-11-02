import json
import os
from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport

# Path to your preprinted certificate template image
TEMPLATE_IMAGE_PATH = r"D:\IF\projects\nikahnama_app\images\nikahnama_preprint_blank.png"  # Update path accordingly

# Default field positions if no file exists
DEFAULT_FIELDS = {
    "serial_no": {"x": 32, "y": 30},
    "reg_no": {"x": 150, "y": 30},
    "masjid_name": {"x": 25, "y": 38, "w": 160},
    "groom_name": {"x": 35, "y": 78},
    "groom_address": {"x": 35, "y": 86, "w": 165},
    # Add more fields here as needed
}

# Function to load saved field positions from coordinates.json
def load_coordinates():
    if os.path.exists("coordinates.json"):
        with open("coordinates.json", "r") as f:
            return json.load(f)
    else:
        return DEFAULT_FIELDS  # Use default if no file exists

# Function to save field positions to coordinates.json
def save_coordinates(fields):
    with open("coordinates.json", "w") as f:
        json.dump(fields, f, indent=4)

# Interactive Layout Editor Class
class LayoutEditor(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Layout Editor")
        self.setGeometry(100, 100, 800, 600)

        self.fields = load_coordinates()  # Load or use defaults
        self.scene = QtWidgets.QGraphicsScene(self)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        self.view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.view.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.view.setRenderHint(QtGui.QPainter.TextAntialiasing)
        self.view.setSceneRect(0, 0, 210, 297)  # A4 size in mm

        self.load_fields()

        self.save_button = QtWidgets.QPushButton("Save Layout", self)
        self.save_button.clicked.connect(self.save_layout)
        self.save_button.setGeometry(650, 530, 100, 30)

        self.show()

    def load_fields(self):
        # Load template image
        self.image_item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap(TEMPLATE_IMAGE_PATH))
        self.scene.addItem(self.image_item)

        # Create draggable fields based on saved coordinates
        for field, coord in self.fields.items():
            field_item = DraggableField(field, coord)
            field_item.setPos(coord["x"], coord["y"])
            self.scene.addItem(field_item)

    def save_layout(self):
        # Save updated field positions to JSON
        fields_position = {}
        for item in self.scene.items():
            if isinstance(item, DraggableField):
                pos = item.pos()
                fields_position[item.toPlainText()] = {"x": pos.x(), "y": pos.y()}

        save_coordinates(fields_position)
        QtWidgets.QMessageBox.information(self, "Saved", "Layout positions saved successfully!")

class DraggableField(QtWidgets.QGraphicsTextItem):
    def __init__(self, label, position, parent=None):
        super().__init__(label, parent)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setDefaultTextColor(QtCore.Qt.black)
        self.setFont(QtGui.QFont("Arial", 12))
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setPos(position["x"], position["y"])

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self._update_position()

    def _update_position(self):
        pos = self.pos()
        print(f"Updated {self.toPlainText()} position: x={pos.x()}, y={pos.y()}")

# Printing Function
class PrintManager:
    def __init__(self, data):
        self.data = data

    def print_certificate(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setFullPage(True)
        printer.setPageSize(QtPrintSupport.QPrinter.A4)
        dlg = QtPrintSupport.QPrintDialog(printer)
        dlg.setWindowTitle("Select Printer")

        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return

        painter = QtGui.QPainter(printer)
        try:
            self.draw_certificate(painter, printer)
        finally:
            painter.end()

    def draw_certificate(self, painter, printer):
        fields = load_coordinates()  # Get the saved coordinates

        # Setup for the drawing
        painter.fillRect(printer.pageRect(), QtCore.Qt.white)
        image_item = QtGui.QImage(TEMPLATE_IMAGE_PATH)
        target = printer.pageRect()
        painter.drawImage(target, image_item)

        # Set font properties
        font = QtGui.QFont("Arial", 12)
        painter.setFont(font)

        for field, coord in fields.items():
            if field in self.data:
                x, y = coord["x"], coord["y"]
                text = self.data[field]
                painter.drawText(x, y, text)

        print("Printed successfully")

# Example data to print
example_data = {
    "serial_no": "12345",
    "reg_no": "67890",
    "masjid_name": "Masjid Ahle Hadees, Kurla",
    "groom_name": "Ahmed Ali",
    "groom_address": "123 Street, City, Country",
}

# Main Entry Point
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    # If the layout file exists, skip editing and print directly
    if os.path.exists("coordinates.json"):
        print_manager = PrintManager(example_data)
        print_manager.print_certificate()
    else:
        # Otherwise, open the layout editor
        editor = LayoutEditor()

    sys.exit(app.exec_())
