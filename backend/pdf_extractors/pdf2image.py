from pdf2image import convert_from_path
import os
from PIL import Image

def extract_pages_as_images(pdf_path, output_dir):
    """
    Converts each page of a PDF into a separate image file.
    Args:
        pdf_path (str): The path to the input PDF file.
        output_dir (str): The directory to save the extracted images.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Converting PDF {pdf_path} to images...")
    
    # Convert PDF pages to a list of PIL Image objects
    images = convert_from_path(pdf_path)

    for i, image in enumerate(images):
        # Save the image
        image_path = os.path.join(output_dir, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        print(f"Saved page {i + 1} as {image_path}")
        
        # Display the image (optional)
        image.show()

# --- Usage Example ---
if __name__ == "__main__":
    pdf_file_path = "path/to/your/document.pdf"  # Replace with your PDF file
    pdf_file_path = "refinalfollowupactionrequiredforyourprototypedeve (1)/Sunflower Bank - Lease Documents/Sunflower Bank- Lease Amendment No. 2.PDF"
    pdf_file_path = "corrected_document.pdf"
    output_folder = "extracted_images_pdf2image"
    
    # Check if the PDF file exists before running
    if not os.path.exists(pdf_file_path):
        print(f"Error: The PDF file was not found at '{pdf_file_path}'")
    else:
        extract_pages_as_images(pdf_file_path, output_folder)
