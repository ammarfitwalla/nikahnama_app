# 🕌 Nikahnama Certificate Generator

A PyQt5-based desktop application for creating, managing, and printing **Nikah (Marriage) Certificates** with pixel-perfect A4 layouts.

The app allows you to:
- Enter Nikah details via an easy-to-use form
- Store all records in a local SQLite database
- View, edit, or delete saved records
- Print or export professionally formatted certificates (PDF or direct printer)
- Precisely control print layouts using `coordinates.json` and template images

---

## 📁 Project Structure

```
NIKAHNAMA_APP/
│
├── images/                    # Certificate templates & A4 print backgrounds
│   ├── a4_blank_300dpi.png
│   ├── nn_preprint_blank_og_copy.png
│   ├── nikahnama.png
│   └── white_page.png
│
├── output/                    # Generated PDFs / printed certificates
│   ├── certificate_163.pdf
│   └── certificate_12345.pdf
│
├── ui/                        # PyQt5 user interface components
│   ├── nikah_form.py          # Form UI for entering Nikah details
│   ├── records_table.py       # Table view for saved records
│   ├── form_mapper.py         # Maps form fields to coordinate system
│   └── drag_and_place.py      # Utility to visually adjust print coordinates
│
├── coordinates.json           # Field coordinates (in mm) for A4 layout
├── print_layout.py            # Core print engine (handles A4 rendering via QPainter)
├── insert_data_in_db.py       # Handles DB insert/update operations
├── database.py                # SQLite DB setup and connection management
├── main_window.py             # Main PyQt5 window combining form + table
├── main.py                    # Application entry point
├── constants.py               # App-wide constants and shared settings
├── resize_image.py            # Utility for DPI and size adjustments
├── sample_data.json           # Sample record for testing layout
└── README.md
```

---

## ⚙️ Features

### 🧾 Certificate Management
- Add new Nikah certificate entries
- Edit existing records
- Delete unwanted records
- Auto-save all data into SQLite

### 🖨️ Printing System
- Print certificates directly or export to PDF
- Perfect A4 scaling (210×297 mm, 96 DPI)
- Uses template overlay for calibration
- Supports grid overlay for alignment debugging
- Multi-line text and wrapping supported

### 🗺️ Coordinate Mapping
- `coordinates.json` defines exact field positions
- Includes font sizes and text widths
- Adjustable offsets (X/Y) for printer calibration
- `drag_and_place.py` helps visually adjust coordinates

---

## 🧠 How It Works

1. **User fills the form** → data is saved into SQLite
2. **User selects a record** → can edit, delete, or print it
3. **On print**, data flows through:
   ```
   main_window.py → form_mapper.py → print_layout.py
   ```
4. `print_layout.py` renders data on top of the certificate template using `QPainter` and saves to PDF

---

## 🧩 Tech Stack

| Component | Description |
|-----------|-------------|
| **Frontend** | PyQt5 (Forms, Tables, Events) |
| **Database** | SQLite |
| **Printing Engine** | QPainter + QPrinter |
| **Data Layout** | JSON-based coordinate mapping |
| **Language** | Python 3.x |

---

## 🚀 Installation & Usage

### 1️⃣ Install Dependencies
```bash
pip install PyQt5 pillow
```

### 2️⃣ Run the App
```bash
python main.py
```

### 3️⃣ Workflow
1. Fill out Nikah details in the form
2. Click **Save** to store in database
3. Select a record from the table
4. Click **Print** to generate certificate
5. Generated PDFs appear in `/output`

---

## 🧰 Configuration

### 📐 coordinates.json

Defines where each field appears on the A4 page:

```json
{
  "dpi": 300,
  "unit": "millimeters",
  "fields": {
    "serial_no": {
      "x_mm": 32,
      "y_mm": 30,
      "font_size": 11,
      "text_width": -1
    },
    "masjid_name": {
      "x_mm": 25,
      "y_mm": 38,
      "font_size": 11,
      "text_width": 160
    }
  }
}
```

**Parameters:**
- `x_mm`, `y_mm`: Position in millimeters from top-left
- `font_size`: Font size in points
- `text_width`: Maximum width in pixels (-1 for auto)

### 🖼️ Template Image

Replace the background certificate at `/images/nn_preprint_blank.png` to customize your design.

**Requirements:**
- Format: PNG
- Size: A4 at 300 DPI (2480×3508 pixels)
- Color: RGB or RGBA

---

## 🖨️ Output

PDF files are automatically named as:
```
certificate_<serial_number>.pdf
```
and saved in the `/output` directory.

---

## 🎨 Customization

### Adjusting Field Positions
1. Run the form mapper tool from the print dialog
2. Drag text fields to desired positions
3. Click **Save & Print** to update `coordinates.json`
4. Future prints will use the new positions

### Changing Fonts
Edit `print_layout.py` and modify the font family in the drawing functions:
```python
font = QtGui.QFont("Arial", pointSize=pt)  # Change "Arial" to your font
```

---

## 🐛 Troubleshooting

### Fields not aligning properly
- Check DPI settings in `coordinates.json` match your template image
- Use the visual coordinate mapper to adjust positions
- Ensure printer settings are set to "Actual Size" (not "Fit to Page")

### Missing template image
- Verify image path in `coordinates.json`
- Ensure image file exists in `/images` directory
- Check file permissions

### Database errors
- Delete `nikahnama.db` to reset database
- Check write permissions in app directory

---

## 💡 Future Enhancements

- [ ] Multi-page print support
- [ ] Live coordinate calibration tool
- [ ] Export/import database backup
- [ ] Field font style customization
- [ ] Integration with web-based dashboard
- [ ] Batch printing multiple certificates
- [ ] Custom template designer

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Ammar Fitwalla**  
AI & Backend Engineer
📧 [ammarfitwalla@gmail.com](mailto:ammarfitwalla@gmail.com)

---

## 🙏 Acknowledgments

- PyQt5 for the excellent GUI framework
- All contributors and testers

---

> *"Precision printing meets automation — for perfectly aligned Nikahnama certificates."*