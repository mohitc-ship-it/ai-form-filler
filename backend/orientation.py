import pypdf
import os
from pdf2image import convert_from_path
from PIL import Image

def fix_pdf_orientation(pdf_path, output_path):
    """
    Checks each page of a PDF and corrects its orientation if necessary.
    
    Args:
        pdf_path (str): Path to the input PDF.
        output_path (str): Path to save the new, corrected PDF.
    """
    try:
        reader = pypdf.PdfReader(pdf_path)
        writer = pypdf.PdfWriter()
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            w, h = page.mediabox[2], page.mediabox[3] # get width and height
            
            # Rotate landscape pages to portrait (or vice versa depending on logic)
            # This logic assumes height should be greater than width for correct orientation.
            if w > h:
                page.rotate(90) # Rotate the page content 90 degrees
                print(f"Page {page_num + 1} was in landscape, rotated.")
            
            writer.add_page(page)

        # Write the new, corrected PDF to the output path
        with open(output_path, "wb") as f:
            writer.write(f)
        
        print(f"Corrected PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"An error occurred while fixing PDF orientation: {e}")
        return None

def extract_pages_as_images(pdf_path, output_dir):
    """
    Converts each page of a PDF into a separate image file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Converting PDF {pdf_path} to images...")
    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        print(f"Saved page {i + 1} as {image_path}")
        image.show()

# --- Main execution ---
if __name__ == "__main__":
    original_pdf = "userPdfData/refinalfollowupactionrequiredforyourprototypedeve (1)/Sunflower Bank - Lease Documents/Sunflower Bank- Lease Amendment No. 1.PDF"  # Replace with your PDF file
    corrected_pdf = "corrected_document.pdf"
    output_folder = "extracted_images"

    # Step 1: Fix the PDF's orientation
    corrected_pdf_path = fix_pdf_orientation(original_pdf, corrected_pdf)
    
    if corrected_pdf_path:
        # Step 2: Extract images from the corrected PDF
        extract_pages_as_images(corrected_pdf_path, output_folder)
