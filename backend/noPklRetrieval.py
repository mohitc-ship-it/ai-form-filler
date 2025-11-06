import pickle
from base64 import b64decode
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import time
from langchain_openai import OpenAIEmbeddings
import pickle
from langchain_chroma import Chroma
from langchain_core.stores import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os


def create_retriever(db_name,collection_name):
    print("now i am in retriever")
    # persist_dir = "./chroma_db"

    # Load persisted vectorstore
    # vectorstore = Chroma(
    #     persist_directory=persist_dir,
    #     collection_name="multi_modal_rag",
    #     embedding_function=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    vectorstore = Chroma(
        persist_directory=db_name,
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-large")
    )


    # Create InMemoryStore and populate it from pickle
    store = InMemoryStore()

    # Now pass the proper store to the retriever
    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key="doc_id",
    )

    return retriever


import os
import time
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# def rag(query, vectorstore, summary_to_chunk=None, k=5, min_text_chunks=1, llm_provider="openai",structure=None):
#     """
#     RAG pipeline with text and image retrieval.
#     Args:
#         query (str): User query.
#         vectorstore: Chroma/Pinecone/etc.
#         summary_to_chunk: optional mapping fn (unused here).
#         k (int): initial top-k results.
#         min_text_chunks (int): minimum number of text chunks to retrieve.
#         llm_provider (str): "openai" or "gemini"
#     """
#     print(f"\n--- RAG PIPELINE START ---")
#     # print(f"Query: {query}")
#     print("sending doe similarity search")

#     try:
#         # Step 5: Select LLM
#         if llm_provider == "openai":
#             llm = ChatOpenAI(
#                 model="gpt-4o-mini",
#                 temperature=0,
#                 max_retries=2,
#                 api_key=os.getenv("OPENAI_API_KEY"),  # safer: load from env
#             )
#         elif llm_provider == "gemini":
#             llm = ChatGoogleGenerativeAI(
#                 model="gemini-2.5-flash",
#                 temperature=0,
#                 max_retries=2,
#             )
#         else:
#             raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
#         # QUERY_REWRITE_PROMPT = """
#         # You are an assistant helping retrieve legal and compliance documents.

#         # Given a user query, rewrite it into a clear, factual, search-oriented query 
#         # that can best match relevant ordinance or code sections.

#         # - Use formal regulatory language (e.g., "according to", "as defined in", "requirements for").
#         # - Expand abbreviations (e.g., "ADU" → "Accessory Dwelling Unit").
#         # - Include key context if implied (e.g., "plaster" → "plaster or similar wall finish materials").
#         # - Output only one rewritten query, no explanations.

#         # User query: {query}
#         # Rewritten search query:
#         # """


#         # query = llm.invoke(QUERY_REWRITE_PROMPT)
        
#         # Step 1: Similarity search
#         results = vectorstore.similarity_search(query, k=k)
#         # print("result we have ", results)
#         print(f"Similarity search returned: {len(results)}")

#         # Step 2: Map to original chunks
#         retrieved_texts, retrieved_images = [], []

#         for doc in results:
#             chunk = doc.metadata.get("original_content")
           
#             if not chunk:
#                 continue
#             if doc.metadata.get("type") in ["text", "table"]:
#                 retrieved_texts.append(chunk)
#                 print("chunk is ,",retrieved_texts)
#             elif doc.metadata.get("type") == "image":
#                 retrieved_images.append(chunk)

#         # Step 3: Ensure minimum text chunks
#         combined_texts = list(dict.fromkeys(retrieved_texts))  # deduplicate

#         if len(combined_texts) < min_text_chunks:
#             print("Not enough text chunks, expanding search...")
#             more_results = vectorstore.similarity_search(query, k=k * 3)
#             for doc in more_results:
#                 chunk = doc.metadata.get("original_content")
#                 if (
#                     chunk
#                     and doc.metadata.get("type") in ["text", "table"]
#                     and chunk not in combined_texts
#                 ):
#                     combined_texts.append(chunk)
#                     if len(combined_texts) >= min_text_chunks:
#                         break

#         print(f"Retrieved text chunks: {len(combined_texts)}")
#         # print(f"Retrieved image chunks: {len(retrieved_images)}")

#         # Step 4: Prepare messages for LLM
#         content_list = []

#         if combined_texts:
#             context_text = "\n".join(map(str, combined_texts))  # limit to 5 chunks
#             content_list.append({"type": "text", "text": f"Context:\n{context_text}"})

#         print("context list text is ", content_list)
#         # Format images per provider
#         def format_image(img_b64):
#             if llm_provider == "gemini":
#                 # Gemini expects image_url with data URI string
#                 return {"type": "image_url", "image_url": f"data:image/png;base64,{img_b64}"}
#             elif llm_provider == "openai":
#                 # OpenAI expects raw base64 data in a content block
#                 return {
#                     "type": "image",
#                     "source_type": "base64",
#                     "data": img_b64,
#                     "mime_type": "image/png",
#                 }
#             else:
#                 raise ValueError("Unsupported provider for image formatting")

#         print("len of image in context are, " , len(retrieved_images))
#         for img_b64 in retrieved_images:
#             content_list.append(format_image(img_b64))

#         content_list.append({"type": "text", "text": f"Question: {query}"})
#         message_local = HumanMessage(content=content_list)



#         # Step 6: Call LLM with retry
#         for attempt in range(2):  # 2 attempts
#             try:
#                 if(structure):
#                     print("atrructure is ", structure)
#                     llm = llm.with_structured_output(structure)
#                     response = llm.invoke([message_local])
#                     response['source'] = response['source'] + " all uniqyue file names from context chunks"
#                     print("response final is ", response)
#                 else:
#                     response = llm.invoke([message_local])
#                 print("--- RAG PIPELINE END ---\n")
#                 return response
#             except Exception as e:
#                 print(f"Attempt {attempt+1} failed: {e}")
#                 if attempt == 0:
#                     print("Retrying in 60s...")
#                     time.sleep(60)

#         print("All retries failed.")
#         return None
#     except Exception as e:
#         print("excepting is ,",e)
def rag(query, vectorstore, summary_to_chunk=None, k=5, min_text_chunks=1, llm_provider="openai", structure=None):
    """
    RAG pipeline with text and image retrieval.
    Args:
        query (str): User query.
        vectorstore: Chroma/Pinecone/etc.
        summary_to_chunk: optional mapping fn (unused here).
        k (int): initial top-k results.
        min_text_chunks (int): minimum number of text chunks to retrieve.
        llm_provider (str): "openai" or "gemini"
        structure: optional structured output schema
    """
    print(f"\n--- RAG PIPELINE START ---")
    print("sending doe similarity search")

    try:
        # Step 1: Select LLM
        if llm_provider == "openai":
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                max_retries=2,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        elif llm_provider == "gemini":
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                max_retries=2,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

        # Step 2: Similarity search
        results = vectorstore.similarity_search(query, k=k)
        print(f"Similarity search returned: {len(results)}")

        # Step 3: Map to original chunks
        retrieved_texts, retrieved_images, all_file_names = [], [], set()

        for doc in results:
            chunk = doc.metadata.get("original_content")
            file_name = doc.metadata.get("file_name")

            if file_name:
                all_file_names.add(file_name)

            if not chunk:
                continue

            doc_type = doc.metadata.get("type")
            if doc_type in ["text", "table"]:
                retrieved_texts.append(chunk)
            elif doc_type == "image":
                retrieved_images.append(chunk)

        # Step 4: Ensure minimum text chunks
        combined_texts = list(dict.fromkeys(retrieved_texts))
        if len(combined_texts) < min_text_chunks:
            print("Not enough text chunks, expanding search...")
            more_results = vectorstore.similarity_search(query, k=k * 3)
            for doc in more_results:
                chunk = doc.metadata.get("original_content")
                file_name = doc.metadata.get("file_name")

                if file_name:
                    all_file_names.add(file_name)

                if (
                    chunk
                    and doc.metadata.get("type") in ["text", "table"]
                    and chunk not in combined_texts
                ):
                    combined_texts.append(chunk)
                    if len(combined_texts) >= min_text_chunks:
                        break

        print(f"Retrieved text chunks: {len(combined_texts)}")
        print(f"Unique file names from chunks: {list(all_file_names)}")

        # Step 5: Prepare messages for LLM
        content_list = []
        if combined_texts:
            context_text = "\n".join(map(str, combined_texts))
            content_list.append({"type": "text", "text": f"Context:\n{context_text}"})

        def format_image(img_b64):
            if llm_provider == "gemini":
                return {"type": "image_url", "image_url": f"data:image/png;base64,{img_b64}"}
            elif llm_provider == "openai":
                return {
                    "type": "image",
                    "source_type": "base64",
                    "data": img_b64,
                    "mime_type": "image/png",
                }
            else:
                raise ValueError("Unsupported provider for image formatting")

        for img_b64 in retrieved_images:
            content_list.append(format_image(img_b64))

        content_list.append({"type": "text", "text": f"Question: {query}"})
        message_local = HumanMessage(content=content_list)

        # Step 6: Call LLM
        for attempt in range(2):
            try:
                if structure:
                    print("Using structured output with schema:", structure)
                    llm = llm.with_structured_output(structure)
                    response = llm.invoke([message_local])

                    # ✅ Handle both dict and Pydantic model cases
                    if hasattr(response, "model_dump"):  # pydantic v2
                        response = response.model_dump()
                    elif hasattr(response, "dict"):  # pydantic v1
                        response = response.dict()

                    all_file_names.add(response.get("source", ""))
                    # ✅ Add unique file names from metadata
                    response["source"] = list(all_file_names)

                    print("Final structured response:", response)
                else:
                    response = llm.invoke([message_local])


                print("--- RAG PIPELINE END ---\n")
                return response
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                if attempt == 0:
                    print("Retrying in 60s...")
                    time.sleep(2)

        print("All retries failed.")
        return None
    except Exception as e:
        print("Exception:", e)
        return None



# message = "what is vacant hashes or something kinda"
# message2 = "tell about images u have"
# message2 = "what is parcel size"

# # diagram based
# message2 = "How many parking rows are in front of Big Lots?"
# message2 = "Which suites are labeled “Vacant”?"
# message2 = "What is the square footage of Ashley Furniture?"
# message2 = "How many stories are all listed buildings?"
# message2 = "what details we have from vicinity map"
# message2 = "tell me in bullets and in detail about NE Bldg. Corner"



# message2 = "check in images about vacant blocks"
# message2 = "What is the square footage of the leased property?"
from pydantic import BaseModel, Field

class ExtractedField(BaseModel):
    value: str = Field(..., description="The extracted value for the query")
    confidence: float = Field(..., description="Confidence score between 0 and 1")
    source: str = Field(..., description="The document chunk or source name where value was found")
    reason:str = Field(..., description="Explanation of how the value was derived")

message2 = "value of Gross Sales is"
# message2 = "what is exclusive use clause"
message2 = "total leased area in square feet"
message2 = "what is Percentage Rent value"
message2 = "gross sales value is "
# message2 ="""Extract the clause or value related to "Financial Statements" from the provided lease documents.
# Identify if the lease requires the tenant or landlord to deliver any financial statements, profit/loss reports, or sales certifications.
# If no such clause exists, respond with "Not specified" and explain why."""
# message2 = "Radius Restriction"
# message2 = "financial statements"
message2 = " Relocation Clause "
# message2 = "Security Deposit:"
message2 = "Guarantor"
message2 = "use"
message2 = "Term Remaining"
message2 = "annual rent is "

message2 = "what is $122,984.40"
message2 = "term remaining"
message2 = " January 31, 2051"
message2 = "what is term value of this lease"
message2 = "what is radius"
message2 = "what is termination right of this lease"
message2 = "parcel size"
# retriever = create_retriever("./chroma_db_compliance3","surveys_lease_data")
# vectorstore = retriever.vectorstore
# answer = rag(message2, vectorstore,structure=ExtractedField)
# print("answer is ",answer)