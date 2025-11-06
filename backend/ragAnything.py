import os
import json
import asyncio
import datetime
from pathlib import Path
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from lightrag.lightrag import LightRAG  # <-- important import


# --------------------------------------------------
# GLOBAL CONFIGURATION
# --------------------------------------------------
API_KEY = ""
  # Add your key here
BASE_URL = "https://api.openai.com/v1"
WORKING_DIR = "./rag_storage"       # Existing vector DB folder
OUTPUT_ROOT = "./rag_outputs"


# --------------------------------------------------
# GLOBAL INSTANCE CACHE
# --------------------------------------------------
_rag_instance: RAGAnything | None = None


# --------------------------------------------------
# RAG SETUP
# --------------------------------------------------
def get_rag_instance() -> RAGAnything:
    """
    Returns globally cached RAGAnything instance and ensures LightRAG is loaded from disk.
    """
    global _rag_instance
    if _rag_instance is not None:
        return _rag_instance

    config = RAGAnythingConfig(
        working_dir=WORKING_DIR,
        parser="mineru",
        parse_method="auto",
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=False,
    )

    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "gpt-4o-mini",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=API_KEY,
            base_url=BASE_URL,
            **kwargs,
        )

    def vision_model_func(
        prompt,
        system_prompt=None,
        history_messages=[],
        image_data=None,
        messages=None,
        **kwargs,
    ):
        if messages:
            return openai_complete_if_cache(
                "gpt-4o-mini",
                "",
                messages=messages,
                api_key=API_KEY,
                base_url=BASE_URL,
                **kwargs,
            )
        elif image_data:
            return openai_complete_if_cache(
                "gpt-4o",
                "",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                            },
                        ],
                    }
                ],
                api_key=API_KEY,
                base_url=BASE_URL,
                **kwargs,
            )
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)

    embedding_func = EmbeddingFunc(
        embedding_dim=3072,
        max_token_size=8192,
        func=lambda texts: openai_embed(
            texts,
            model="text-embedding-3-large",
            api_key=API_KEY,
            base_url=BASE_URL,
        ),
    )

    # Initialize RAGAnything
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
    )

    # ✅ Ensure the underlying LightRAG loads your existing DB
    try:
        rag.lightrag = LightRAG(
            working_dir=WORKING_DIR,
            embedding_func=embedding_func,
            llm_model_func=llm_model_func,
        )
        print("✅ Loaded existing LightRAG vector DB successfully.")
    except Exception as e:
        print(f"⚠️ Could not load existing LightRAG DB: {e}")

    _rag_instance = rag
    return rag


# --------------------------------------------------
# STRUCTURED OUTPUT PIPELINE
# --------------------------------------------------
async def structured_output_pipeline(base_text: str, schema: dict):
    system_prompt = f"""
    You are an expert data formatter.
    Convert the following RAG output into a structured JSON object
    that strictly follows this schema:
    {json.dumps(schema, indent=2)}

    Output valid JSON only.
    """

    result = openai_complete_if_cache(
        "gpt-4o-mini",
        base_text,
        system_prompt=system_prompt,
        api_key=API_KEY,
        base_url=BASE_URL,
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(result.strip())
    except Exception:
        return {"error": "Failed to parse JSON", "raw_output": result}


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def create_dynamic_output_dir(prefix: str) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_path = Path(OUTPUT_ROOT) / f"{prefix}_{timestamp}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return str(dir_path)


def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --------------------------------------------------
# DOCUMENT STORAGE
# --------------------------------------------------
async def store_document(file_path: str):
    rag = get_rag_instance()
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    file_name = os.path.basename(file_path)
    output_dir = create_dynamic_output_dir(Path(file_name).stem)

    try:
        print(f"📄 Processing: {file_name}")
        result = await rag.process_document_complete(
            file_path=file_path,
            output_dir=output_dir,
        )
        print(f"✅ Stored: {file_name}")
        return result
    except Exception as e:
        print(f"❌ Error processing {file_name}: {e}")
        return None


# --------------------------------------------------
# QUERY FUNCTION
# --------------------------------------------------
async def query_rag(
    question: str,
    structured_schema: dict | None = None,
    mode: str = "hybrid",
    max_results: int = 5,
    temperature: float = 0.2,
    top_k: int = 3,
    with_sources: bool = True,
):
    rag = get_rag_instance()

    if not hasattr(rag, "lightrag") or not rag.lightrag:
        print("⚠️ No LightRAG instance found. Please process a document first.")
        return None

    if not os.path.exists(WORKING_DIR) or not os.listdir(WORKING_DIR):
        print("⚠️ No documents found in working_dir. Please process documents first.")
        return None

    if not question.strip():
        print("⚠️ Empty query provided.")
        return None

    output_dir = create_dynamic_output_dir("query")

    try:
        print(f"\n🔍 Query: {question}")
        base_result = await rag.aquery(
            question,
            mode=mode,
            top_k=top_k,
        )

        if structured_schema:
            print("🧩 Running structured output layer...")
            structured_result = await structured_output_pipeline(
                json.dumps(base_result, ensure_ascii=False),
                structured_schema,
            )
        else:
            structured_result = base_result

        save_json(
            {
                "question": question,
                "timestamp": datetime.datetime.now().isoformat(),
                "base_result": base_result,
                "structured_result": structured_result,
            },
            os.path.join(output_dir, "query_result.json"),
        )

        print(f"💬 Result saved at {output_dir}")
        return structured_result

    except Exception as e:
        print(f"❌ Query error: {e}")
        return None


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------
async def main(file_name: str | None = None):
    # Uncomment if you want to add new docs
    # if file_name:
    #     await store_document(file_path=file_name)

    # await query_rag("What utilities are included in the lease?")
    await query_rag("what is date of lease made")
    pass


if __name__ == "__main__":
    file_name = None
    asyncio.run(main(file_name))
