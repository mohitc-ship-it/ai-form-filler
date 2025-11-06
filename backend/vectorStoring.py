from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import CompositeElement, Image as UImage, Table
from PIL import Image
from langchain_core.documents import Document
import base64
from io import BytesIO
import os
import pickle
import uuid

from summaries import summariesData, summariesImages

# --- Minimum size to filter unwanted images ---
MIN_WIDTH = 1000
MIN_HEIGHT = 1000

# --- Convert base64 to PIL Image ---
def base64_to_pil(b64_str):
    if not b64_str:
        return None
    try:
        return Image.open(BytesIO(base64.b64decode(b64_str)))
    except Exception as e:
        print("Failed to convert image:", e)
        return None

# --- Convert PIL Image to base64 string ---
def pil_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# --- Extract and filter images from chunks ---
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

# --- Chunk PDF and show filtered images ---
def chunking(file_path, show_images=True):
    print("Chunking PDF:", file_path)

    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=True,
        strategy="hi_res",
        extract_image_block_types=["Image"],  # important to detect images
        extract_image_block_to_payload=True,
        chunking_strategy="by_title",
        max_characters=10000,
        combine_text_under_n_chars=2000,
        new_after_n_chars=6000,
    )

    # chunks = partition_pdf(
    #     filename=file_path,
    #     infer_table_structure=True,  # still extract tables
    #     strategy="hi_res",
    #     extract_image_block_types=[],  # no images
    #     extract_image_block_to_payload=False,
    #     chunking_strategy="by_title",
    #     max_characters=10000,
    #     combine_text_under_n_chars=2000,
    #     new_after_n_chars=6000,
    # )

    images_b64, images_pil = get_images_from_chunks(chunks)
    print(f"Found {len(images_pil)} filtered images (>{MIN_WIDTH}x{MIN_HEIGHT}px)")

    # Optionally show images
    if show_images:
        for idx, img in enumerate(images_pil):
            print(f"Displaying image {idx+1}: size={img.size}")
            img.show()

    return chunks, images_b64, images_pil

# --- Store chunked data in vectorstore ---
def storing(file_path, retriever, vectorstore):
    print("Will be storing data...")

    # Step 1: Chunk the document
    chunks, images_b64, images_pil = chunking(file_path, show_images=False)
    print("Done chunking")
    print("Total chunks:", len(chunks), "Filtered images:", len(images_pil))

    # Separate chunks into texts and tables
    texts = []
    tables = []
    for chunk in chunks:
        if "Table" in str(type(chunk)):
            tables.append(chunk)
        elif "CompositeElement" in str(type(chunk)):
            texts.append(chunk)

    print("Text chunks:", len(texts), "Table chunks:", len(tables))

    # Step 2: Generate summaries
    text_summaries, table_summaries = summariesData(texts, tables)

    # Convert images to base64 before sending to summariesImages
    images_b64_for_summary = [pil_to_base64(img) for img in images_pil]
    image_summaries = summariesImages(images_b64_for_summary)

    # Step 3: Initialize mapping dictionary
    summary_to_chunk = {}
    id_key = retriever.id_key

    # Step 4: Add text summaries
    for summary, chunk in zip(text_summaries, texts):
        doc_id = str(uuid.uuid4())
        chunk_content = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
        metadata = {
            id_key: doc_id,
            "type": "text",
            "original_content": chunk_content,
            "file_name": os.path.basename(file_path)
        }
        summary_doc = Document(page_content=summary, metadata=metadata)
        retriever.vectorstore.add_documents([summary_doc])
        retriever.docstore.mset([(doc_id, {"content": chunk_content})])
        summary_to_chunk[doc_id] = chunk_content

    # Step 5: Add table summaries
    for summary, chunk in zip(table_summaries, tables):
        doc_id = str(uuid.uuid4())
        chunk_content = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)
        metadata = {
            id_key: doc_id,
            "type": "table",
            "original_content": chunk_content,
            "file_name": os.path.basename(file_path)
        }
        summary_doc = Document(page_content=summary, metadata=metadata)
        retriever.vectorstore.add_documents([summary_doc])
        retriever.docstore.mset([(doc_id, {"content": chunk_content})])
        summary_to_chunk[doc_id] = chunk_content

    # Step 6: Add image summaries
    for summary, img in zip(image_summaries, images_pil):
        doc_id = str(uuid.uuid4())
        chunk_content = pil_to_base64(img)

        if hasattr(summary, "content"):
            summary_text = summary.content
        else:
            summary_text = str(summary)

        metadata = {
            id_key: doc_id,
            "type": "image",
            "original_content": chunk_content,
            "file_name": os.path.basename(file_path)
        }

        summary_doc = Document(page_content=summary_text, metadata=metadata)
        retriever.vectorstore.add_documents([summary_doc])
        retriever.docstore.mset([(doc_id, {"content": chunk_content})])
        summary_to_chunk[doc_id] = chunk_content

    # Step 7: Persist mapping
    with open("summary_to_chunk.pkl", "wb") as f:
        pickle.dump(summary_to_chunk, f)

    print("Data added to vector DB and mapping saved.")
    print("Total entries in summary_to_chunk:", len(summary_to_chunk))
    return summary_to_chunk, retriever
