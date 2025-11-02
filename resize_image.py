# from PIL import Image

# # A4 at 300 DPI
# width_px, height_px = 2480, 3508

# # Create a blank white image
# img = Image.new("RGB", (width_px, height_px), "white")

# # Add DPI metadata
# img.save("a4_blank_300dpi.png", dpi=(300, 300))
# print("Saved a4_blank_300dpi.png successfully.")

from PIL import Image

# === Paths ===
src_path = "images/nn_preprint_blank_og.png"      # your current image
dst_path = "images/nn_preprint_a4_300dpi.png"  # output image

# === A4 size at 300 DPI ===
A4_SIZE_PX = (2480, 3508)  # width x height

# === Load original image ===
img = Image.open(src_path).convert("RGB")

# === Resize proportionally to fit A4 ===
# This ensures your certificate fits nicely inside A4 without distortion
img.thumbnail(A4_SIZE_PX, Image.LANCZOS)

# === Create blank A4 canvas (white) ===
a4_canvas = Image.new("RGB", A4_SIZE_PX, "white")

# === Center the original image on the A4 canvas ===
x = (A4_SIZE_PX[0] - img.width) // 2
y = (A4_SIZE_PX[1] - img.height) // 2
a4_canvas.paste(img, (x, y))

# === Save with 300 DPI metadata ===
a4_canvas.save(dst_path, dpi=(300, 300))
print(f"✅ Saved A4 version at 300 DPI → {dst_path}")
print(f"Original image size: {img.size}, A4 canvas size: {A4_SIZE_PX}")
# === Done ===  
print("✅ Done resizing and centering image on A4 canvas.")