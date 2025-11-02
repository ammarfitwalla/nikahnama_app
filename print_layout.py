# print_layout.py
from PyQt5 import QtCore, QtGui, QtPrintSupport
import os
import json

# -------- Default print profile (A4) - FALLBACK ----------
DEFAULT_PROFILE = {
    "page_size_mm": [210, 297],
    "font_family": "Times New Roman",
    "default_pt": 11,
    "fields": {}  # Will be loaded from coordinates.json
}

def _mm_to_px(mm: float, dpi: float) -> int:
    return int((mm / 25.4) * dpi)

# def _one_line(text: str) -> str:
#     if not text:
#         return ""
#     return " ".join(str(text).split())

# Preserve newlines, only normalize spaces/tabs on each line
def _one_line(text: str) -> str:
    if not text:
        return ""
    lines = str(text).split('\n')
    return '\n'.join(' '.join(line.split()) for line in lines)

# Or just remove the function call entirely if you want to preserve all whitespace
# def _draw_text_mm(painter, x_mm, y_mm, text, pt, family, max_w_mm=None, align=QtCore.Qt.AlignLeft):
#     if not text:
#         return
#     font = QtGui.QFont(family, pointSize=pt)
#     painter.setFont(font)
#     metrics = QtGui.QFontMetrics(font)
#     x = _mm_to_px(x_mm, painter.device().logicalDpiX())
#     y = _mm_to_px(y_mm, painter.device().logicalDpiY())
#     if max_w_mm is None:
#         painter.drawText(x, y, text)
#     else:
#         rect = QtCore.QRect(
#             x, y - metrics.ascent(),
#             _mm_to_px(max_w_mm, painter.device().logicalDpiX()),
#             metrics.height()
#         )
#         painter.drawText(rect, align, text)

def _draw_text_mm(painter, x_mm, y_mm, text, pt, family, max_w_mm=None, align=QtCore.Qt.AlignLeft):
    if not text:
        return
    font = QtGui.QFont(family, pointSize=pt)
    painter.setFont(font)
    metrics = QtGui.QFontMetrics(font)
    x = _mm_to_px(x_mm, painter.device().logicalDpiX())
    y = _mm_to_px(y_mm, painter.device().logicalDpiY())
    if max_w_mm is None:
        # For single point drawing, we need to handle multiline manually
        # or draw within a large bounding rect
        rect = QtCore.QRect(x, y - metrics.ascent(), 10000, 10000)
        painter.drawText(rect, align | QtCore.Qt.TextExpandTabs, text)
    else:
        rect = QtCore.QRect(
            x, y - metrics.ascent(),
            _mm_to_px(max_w_mm, painter.device().logicalDpiX()),
            metrics.height()
        )
        # Add flags to expand tabs and preserve newlines
        painter.drawText(rect, align | QtCore.Qt.TextExpandTabs, text)

def _draw_grid_mm(painter, page_w_mm, page_h_mm, step_mm=10):
    pen = QtGui.QPen(QtGui.QColor(200, 200, 200))
    pen.setStyle(QtCore.Qt.DotLine)
    painter.setPen(pen)
    dpi_x = painter.device().logicalDpiX()
    dpi_y = painter.device().logicalDpiY()
    for x in range(0, int(page_w_mm)+1, step_mm):
        painter.drawLine(_mm_to_px(x, dpi_x), _mm_to_px(0, dpi_y),
                         _mm_to_px(x, dpi_x), _mm_to_px(page_h_mm, dpi_y))
    for y in range(0, int(page_h_mm)+1, step_mm):
        painter.drawLine(_mm_to_px(0, dpi_x), _mm_to_px(y, dpi_y),
                         _mm_to_px(page_w_mm, dpi_x), _mm_to_px(y, dpi_y))

def _draw_template_background(painter, printer, img_path, page_w_mm, page_h_mm):
    if not img_path or not os.path.exists(img_path):
        return
    img = QtGui.QImage(img_path)
    if img.isNull():
        return
    target = printer.pageRect()
    painter.setOpacity(0.18)
    painter.drawImage(target, img)
    painter.setOpacity(1.0)

def load_coordinates_profile(coords_file):
    """
    Load field coordinates from JSON file and convert to print profile format
    
    Args:
        coords_file: Path to coordinates JSON file
        
    Returns:
        dict: Print profile with coordinates
    """
    if not os.path.exists(coords_file):
        raise FileNotFoundError(f"Coordinates file not found: {coords_file}")
    
    with open(coords_file, 'r') as f:
        coords_data = json.load(f)
    
    # Build profile from coordinates
    profile = {
        "page_size_mm": [210, 297],  # Default A4
        "font_family": "Times New Roman",
        "default_pt": 11,
        "fields": {}
    }
    
    fields = coords_data.get("fields", {})
    for field_id, field_info in fields.items():
        print(field_id, field_info)
        profile["fields"][field_id] = {
            field_id: field_info.get("text", ""),
            "x": field_info["x_mm"],
            "y": field_info["y_mm"],
            "pt": field_info.get("font_size", 11),
            "w": field_info.get("text_width", -1) if field_info.get("text_width", -1) != -1 else None
        }
    
    return profile

def draw_certificate_from_coords(
    painter: QtGui.QPainter,
    printer: QtPrintSupport.QPrinter,
    data: dict,
    *,
    coords_file: str = "coordinates.json",
    show_template: bool = False,
    template_path: str = None,
    offset_x_mm: float = 0.0,
    offset_y_mm: float = 0.0,
    debug_grid: bool = False,
):
    """
    Renders text onto a blank page using coordinates from JSON file
    
    Args:
        painter: QPainter object
        printer: QPrinter object
        data: Dictionary with field data to print
        coords_file: Path to coordinates JSON file (default: "coordinates.json")
        show_template: Show background template for calibration
        template_path: Path to template image
        offset_x_mm: X offset in millimeters
        offset_y_mm: Y offset in millimeters
        debug_grid: Show grid for calibration
    """
    # Load profile from coordinates file
    try:
        profile = load_coordinates_profile(coords_file)
    except FileNotFoundError:
        raise Exception(f"Coordinates file not found: {coords_file}. Please configure layout first.")
    
    page_w_mm, page_h_mm = profile.get("page_size_mm", [210, 297])

    # Set paper size
    try:
        printer.setPaperSize(QtCore.QSizeF(page_w_mm, page_h_mm), QtPrintSupport.QPrinter.Millimeter)
    except Exception:
        pass
    printer.setFullPage(True)

    # White background
    print(show_template, template_path)
    if not (show_template and template_path):
        print('fill with white')
        painter.fillRect(printer.pageRect(), QtCore.Qt.white)

    # Optional: template
    if show_template and template_path:
        _draw_template_background(painter, printer, template_path, page_w_mm, page_h_mm)

    # Optional: grid
    if debug_grid:
        _draw_grid_mm(painter, page_w_mm, page_h_mm, step_mm=10)

    # Draw each field using coordinates
    family = profile.get("font_family", "Times New Roman")
    default_pt = profile.get("default_pt", 11)
    print(profile["fields"])
    for key, spec in profile["fields"].items():
        val = _one_line(spec.get(key, ""))
        print(f"key={key}, val={val}")
        if not val:
            continue
        x = spec.get("x", 0.0) + offset_x_mm
        y = spec.get("y", 0.0) + offset_y_mm
        pt = spec.get("pt", default_pt)
        w = spec.get("w")  # may be None
        _draw_text_mm(painter, x, y, val, pt, family, max_w_mm=w)


def draw_certificate(
    painter: QtGui.QPainter,
    printer: QtPrintSupport.QPrinter,
    data: dict,
    *,
    profile: dict = None,
    show_template: bool = False,
    template_path: str = None,
    offset_x_mm: float = 0.0,
    offset_y_mm: float = 0.0,
    debug_grid: bool = False,
):
    """
    LEGACY: Renders text using hardcoded profile (for backward compatibility)
    Use draw_certificate_from_coords() for coordinate-based printing
    """
    prof = profile or DEFAULT_PROFILE
    page_w_mm, page_h_mm = prof.get("page_size_mm", [210, 297])

    try:
        printer.setPaperSize(QtCore.QSizeF(page_w_mm, page_h_mm), QtPrintSupport.QPrinter.Millimeter)
    except Exception:
        pass
    printer.setFullPage(True)


    # White background 
    if not (show_template and template_path):
        painter.fillRect(printer.pageRect(), QtCore.Qt.white)

    if show_template and template_path:
        _draw_template_background(painter, printer, template_path, page_w_mm, page_h_mm)

    if debug_grid:
        _draw_grid_mm(painter, page_w_mm, page_h_mm, step_mm=10)

    family = prof.get("font_family", "Times New Roman")
    default_pt = prof.get("default_pt", 11)

    for key, spec in prof["fields"].items():
        val = _one_line(data.get(key, ""))
        if not val:
            continue
        x = spec.get("x", 0.0) + offset_x_mm
        y = spec.get("y", 0.0) + offset_y_mm
        pt = spec.get("pt", default_pt)
        w = spec.get("w")
        _draw_text_mm(painter, x, y, val, pt, family, max_w_mm=w)


# Example usage
if __name__ == "__main__":
    from PyQt5 import QtWidgets, QtPrintSupport
    import sys, os

    app = QtWidgets.QApplication(sys.argv)

    # Sample data
    sample_data = {
        "serial_no": "163",
        "reg_no": "MSBW/MUM/169/2010",
        "masjid_name": "Masjid Ahle Hadees, Kurla",
        "hijri_date": "5th Rajab",
        "eng_date": "27 Jan 2023",
        "nikah_time": "After Maghrib",
        "place_of_nikah": "G. S. P. Ms. Marathi Vidyalaya, Near Pantnagar Bus Depot",
        "groom_name": "Ammar s/o Ishaque Ibrahim Fitwalla",
        "groom_age": "27 yrs",
        "bride_name": "Samreen d/o Riyazuddin Patel",
        "bride_age": "25 yrs",
    }

    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    serial = sample_data.get("serial_no", "0000")
    output_path = os.path.join(output_dir, f"certificate_{serial}.pdf")

    printer = QtPrintSupport.QPrinter()
    printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
    printer.setOutputFileName(output_path)
    printer.setFullPage(True)
    printer.setPaperSize(QtCore.QSizeF(210, 297), QtPrintSupport.QPrinter.Millimeter)
    printer.setOrientation(QtPrintSupport.QPrinter.Portrait)

    painter = QtGui.QPainter()
    if not painter.begin(printer):
        print("❌ Failed to open printer for PDF output")
        sys.exit(1)

    # Use coordinate-based printing
    try:
        draw_certificate_from_coords(
            painter,
            printer,
            sample_data,
            coords_file="coordinates.json",
            show_template=True,
            template_path='images/nn_preprint_blank.png',  #"images/white_page.png",
            debug_grid=True,
            offset_x_mm=0.0,
            offset_y_mm=0.0
        )
        print(f"✅ Certificate saved successfully to:\n{output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

    painter.end()
    painter.save("certificate_preview.png")
    sys.exit(0)