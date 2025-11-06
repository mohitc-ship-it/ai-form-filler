
import glob
import os
import subprocess
from PIL import Image

# 1. Define input and output paths
pdf_path = "refinalfollowupactionrequiredforyourprototypedeve (1)/Salina 2015 Survey- FINAL- 05282015.pdf"  # Replace with your PDF file
pdf_path = "refinalfollowupactionrequiredforyourprototypedeve (1)/Sunflower Bank - Lease Documents/Sunflower Bank- Lease Amendment No. 1.PDF"
pdf_path ="corrected_document.pdf"
output_dir = "output_folder"
output_md_file = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + '.md')
# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Run Marker as a command-line tool with the corrected arguments
print("Processing PDF and extracting images...")
try:
    subprocess.run(
        ["marker_single", pdf_path, "--output_dir", output_dir],
        check=True,
        capture_output=True,
        text=True
    )
    print("Conversion complete. Images saved to:", output_dir)
except subprocess.CalledProcessError as e:
    print(f"Marker command failed: {e.stderr}")
    exit()

# 3. Find and display the extracted images
# Marker saves images to the specified output directory.
image_files = glob.glob(os.path.join(output_dir, "*.png"))  # Can also be *.jpg

if image_files:
    print("\nDisplaying extracted images...")
    for img_path in image_files:
        try:
            with Image.open(img_path) as img:
                print(f"Opening {os.path.basename(img_path)}...")
                img.show()
        except Exception as e:
            print(f"Could not open image {img_path}: {e}")
else:
    print("\nNo images were extracted from the PDF.")