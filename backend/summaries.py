from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Helper to convert images to base64
def convert_image(img):
    if isinstance(img, str):
        return img
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def summariesData(texts, tables, provider="openai"):
    # prompt_text = """
    # You are an assistant tasked with summarizing tables and text.
    # Give a concise summary of the table or text.

    # Respond only with the summary, no additional comment.
    # Do not start your message by saying "Here is a summary" or anything like that.
    # Just give the summary as it is.

    # Table or text chunk: {element}
    # """
    prompt_text = """
    You are an assistant summarizing compliance documents (text or tables). 
    For the given content, extract the following:

    1. Section or ordinance number (if any)
    2. Topic or subject
    3. Key definitions, rules, limits, or numeric values
    4. Purpose or policy rationale (if stated)
    5. Conditional rules, exceptions, or special notes

    Respond only in concise, structured bullet points.
    Do not add any commentary or preamble.
    Content: {element}
    """


    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )
        prompt = ChatPromptTemplate.from_template(prompt_text)
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_retries=2,
            # Use environment variables for keys in real code
        )
        prompt = ChatPromptTemplate.from_template(prompt_text)
    else:
        raise ValueError("Provider must be 'openai' or 'gemini'")
    
    summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

    # Summarize text
    text_summaries = summarize_chain.batch(texts, {"max_concurrency": 3})

    # Summarize tables (as HTML text metadata)
    tables_html = [table.metadata.text_as_html for table in tables]
    table_summaries = summarize_chain.batch(tables_html, {"max_concurrency": 3})

    return text_summaries, table_summaries

# def summariesImages(images, provider="openai"):
#     if provider == "gemini":
#         from langchain_google_genai import ChatGoogleGenerativeAI

#         model = ChatGoogleGenerativeAI(
#             model="gemini-2.5-flash",
#             temperature=0,
#             max_tokens=None,
#             timeout=None,
#             max_retries=2,
#         )

#         def format_image(image):
#             # Gemini expects 'image_url' with 'url' key holding data URI string
#             return {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}

#     elif provider == "openai":
#         from langchain_openai import ChatOpenAI

#         model = ChatOpenAI(
#             model="gpt-4o-mini",
#             temperature=0,
#             max_tokens=None,
#             timeout=None,
#             max_retries=2,
#         )

#         def format_image(image):
#             # OpenAI expects type 'image' with source_type 'base64'
#             return {
#                 "type": "image",
#                 "source_type": "base64",
#                 "data": image,
#                 "mime_type": "image/jpeg",
#             }

#     else:
#         raise ValueError("Provider must be 'openai' or 'gemini'")

#     print(f"summaries of images with {provider}")

#     prompt_text = (
#         "Describe the image in detail. For context, the image is part of a research paper "
#         "explaining the transformers architecture. Be specific about graphs, such as bar plots."
#     )

#     image_summaries = []

#     for img_b64 in images:
#         # Compose message content list for chat input
#         message_content = [
#             {"type": "text", "text": prompt_text},
#             format_image(img_b64)  # Use the appropriate formatted image dict
#         ]

#         # Create a HumanMessage with the content list
#         from langchain.schema import HumanMessage
#         message = HumanMessage(content=message_content)

#         # Call the model's invoke function with the message list containing one HumanMessage
#         result = model.invoke([message])

#         image_summaries.append(result)

#     print("image summaries are done")
#     return image_summaries



# import base64
# from PIL import Image
# import io
# import pillow_avif # Enables PIL to open AVIF files

# def convert_image(file_path):
#     """
#     Opens an image file, converts it to PNG format in memory, and returns
#     the Base64-encoded string with the required data URI prefix.
#     """
#     if isinstance(file_path, str):
#         try:
#             # Open the AVIF file using Pillow
#             with Image.open(file_path) as img:
#                 # Convert the image to PNG bytes in memory
#                 buffer = io.BytesIO()
#                 img.save(buffer, format="PNG")
#                 png_bytes = buffer.getvalue()

#             # Encode the PNG bytes to Base64
#             encoded_string = base64.b64encode(png_bytes).decode('utf-8')
            
#             # Add the required data URI prefix and return
#             return f"data:image/png;base64,{encoded_string}"
#         except FileNotFoundError:
#             return {"error": "File not found."}
#         except Exception as e:
#             return {"error": str(e)}
#     else:
#         return {"error": "Invalid input: expected file path."}

# # Example usage with your AVIF file
# images = ["premium_photo-1683910767532-3a25b821f7ae.avif"]
# image = convert_image(images[0])

# # This will print the complete and correctly formatted Base64 string
# # print("Base64 is ", image)
# print(summariesImages([image]))


import base64
from PIL import Image
import io
import pillow_avif  # Enables PIL to open AVIF files
from langchain_core.messages import HumanMessage

def convert_image(file_path):
    """
    Opens an image file, converts it to PNG format in memory, and returns
    the Base64-encoded string WITHOUT the data URI prefix.
    """
    if isinstance(file_path, str):
        try:
            with Image.open(file_path) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                png_bytes = buffer.getvalue()

            encoded_string = base64.b64encode(png_bytes).decode('utf-8')
            return encoded_string  # Return only base64 string, no prefix
        except FileNotFoundError:
            return {"error": "File not found."}
        except Exception as e:
            return {"error": str(e)}
    else:
        return {"error": "Invalid input: expected file path."}

def summariesImages(images, provider="openai"):
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        def format_image(image):
            # Gemini expects data URI in url field, base64 part only
            return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}}

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        def format_image(image):
            # OpenAI expects base64 without prefix in data field
            return {
                "type": "image",
                "source_type": "base64",
                "data": image,
                "mime_type": "image/png",
            }

    else:
        raise ValueError("Provider must be 'openai' or 'gemini'")

    print(f"summaries of images with {provider}")

    # prompt_text = (
    #     "Describe the image in detail. "
    #     "its a part of compliance documents",
    # )

    prompt_text = """
    You are an assistant summarizing images from compliance documents.
    Describe the image concisely, including:
    - Type of image (flowchart, diagram, map, chart,...etc)
    - Sections, rules, or codes depicted
    - Key relationships, conditional rules, or thresholds
    - Any numeric values or examples shown

    Respond only in concise bullet points.
    Image description: {element}
    """

    image_summaries = []

    for img_b64 in images:
        message_content = [
            {"type": "text", "text": prompt_text},
            format_image(img_b64),
        ]

        message = HumanMessage(content=message_content)
        result = model.invoke([message])
        image_summaries.append(result)

    print("image summaries are done")
    return image_summaries


# Example usage
# images = ["premium_photo-1683910767532-3a25b821f7ae.avif"]
# image_base64 = convert_image(images[0])  # Returns base64 string without URI prefix

# if isinstance(image_base64, dict) and "error" in image_base64:
#     print(f"Error converting image: {image_base64['error']}")
# else:
#     summaries = summariesImages([image_base64], provider="openai")  # or "gemini"
#     print(summaries)
