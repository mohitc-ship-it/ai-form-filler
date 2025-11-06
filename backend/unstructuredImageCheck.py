from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import CompositeElement, Image as UImage, Table
from PIL import Image
import base64
import io
import os

MIN_WIDTH = 00   # ignore images smaller than this width
MIN_HEIGHT = 00  # ignore images smaller than this height

# --- Convert base64 to PIL Image ---
def base64_to_pil(b64_str):
    if not b64_str:
        return None
    try:
        return Image.open(io.BytesIO(base64.b64decode(b64_str)))
    except Exception as e:
        print("Failed to convert image:", e)
        return None

# --- Extract and filter images ---
def get_images_from_chunks(chunks):
    images_b64 = []
    images_pil = []
    for chunk in chunks:
        if isinstance(chunk, CompositeElement):
            for el in getattr(chunk.metadata, "orig_elements", []):
                if isinstance(el, UImage):
                    b64 = el.metadata.image_base64
                    img = base64_to_pil(b64)
                    if img:
                        w, h = img.size
                        if w >= MIN_WIDTH and h >= MIN_HEIGHT:
                            images_b64.append(b64)
                            images_pil.append(img)
    return images_b64, images_pil

# --- Chunk PDF and separate tables/texts, show filtered images ---
def chunking_and_show_images(file_path, show_images=True):
    print("Chunking PDF:", file_path)

    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=True,
        strategy="hi_res",
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True,
        chunking_strategy="by_title",
        max_characters=10000,
        combine_text_under_n_chars=2000,
        new_after_n_chars=6000,
    )

    # Separate chunks into texts and tables
    texts = []
    tables = []
    for chunk in chunks:
        if "Table" in str(type(chunk)):
            tables.append(chunk)
        elif isinstance(chunk, CompositeElement):
            texts.append(chunk)

    # Extract and filter images
    images_b64, images_pil = get_images_from_chunks(chunks)
    print(f"Found {len(images_pil)} filtered images (>{MIN_WIDTH}x{MIN_HEIGHT}px)")

    # Show filtered images
    if show_images:
        for idx, img in enumerate(images_pil):
            print(f"Image {idx+1}: size={img.size}")
            img.show()

    return chunks, texts, tables, images_b64, images_pil

# --- Example usage ---
if __name__ == "__main__":
    file_path = "refinalfollowupactionrequiredforyourprototypedeve (1)/Sunflower Bank - Lease Documents/Sunflower Bank- Lease Amendment No. 1.PDF"
    file_path = "corrected_document.pdf"
    chunks, texts, tables, images_b64, images_pil = chunking_and_show_images(file_path)
    # print(texts[0])
    for text in range(len(texts)):
        print(texts[text])
    print(f"Total chunks: {len(chunks)}, Texts: {len(texts)}, Tables: {len(tables)}, Filtered images: {len(images_pil)}")
