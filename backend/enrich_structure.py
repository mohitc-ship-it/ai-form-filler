import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from llm import llm_structured   # your existing structured LLM helper


# ============================================================
# ✅ Schema (unchanged)
# ============================================================

class FieldEnriched(BaseModel):
    field_text: str = Field(..., description="Field or label text, e.g., 'Tenant Name'")
    context_snippet: Optional[str] = Field(None, description="Nearby or semantic context from document text")
    rag_query: Optional[str] = Field(None, description="Query string to retrieve this field value from vector DB")
    confidence: float = Field(..., description="Confidence score (0–1) in field correctness and completeness")


class TableEnriched(BaseModel):
    table_name: Optional[str] = Field(None, description="Name or inferred purpose of the table")
    columns: List[str] = Field(..., description="Detected or inferred column headers")
    context_snippet: Optional[str] = Field(None, description="Nearby or semantic context for this table")
    rag_query: Optional[str] = Field(None, description="Query string to retrieve this table's data")
    confidence: float = Field(..., description="Confidence score (0–1) in table correctness and completeness")


class EnrichedDocument(BaseModel):
    verified_fields: List[FieldEnriched] = Field(default_factory=list)
    verified_tables: List[TableEnriched] = Field(default_factory=list)

import json
from pathlib import Path
from dataclasses import asdict, is_dataclass

def to_serializable(obj):
    """
    Recursively convert a complex DocumentStructure-like object into
    something JSON serializable (dicts, lists, strings, numbers).
    """
    if obj is None:
        return None

    # Handle dataclasses (common for structured models)
    if is_dataclass(obj):
        return {k: to_serializable(v) for k, v in asdict(obj).items()}

    # Handle pathlib.Path
    if isinstance(obj, Path):
        return str(obj)

    # Handle lists/tuples
    if isinstance(obj, (list, tuple)):
        return [to_serializable(v) for v in obj]

    # Handle dicts
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}

    # Handle custom classes (with __dict__)
    if hasattr(obj, "__dict__"):
        return {k: to_serializable(v) for k, v in vars(obj).items()}

    # Fallback — primitives
    return obj


# ============================================================
# 🧠 Core enrichment function — now supports multi-page
# ============================================================

# def enrich_structure(structure_json_path: str, output_path: str = "enriched_structure.json"):
def enrich_structure(structure_json: dict, output_path: str = "enriched_structure.json"):
    """
    Reads raw structure.json, sends each page to LLM for enrichment,
    and saves a combined enriched_structure.json.
    """
    print("type ", type(structure_json))
    print("structure_json ", structure_json)
    # if not os.path.exists(structure_json_path):
    #     raise FileNotFoundError(f"❌ Input file not found: {structure_json_path}")

    # print(f"📖 Reading structure from {structure_json_path}")
    # with open(structure_json_path, "r", encoding="utf-8") as f:
    #     structure_text = f.read()
    #     structure_json = json.loads(structure_text)
    structure_json = to_serializable(structure_json)

    file_name = structure_json.get("file_name", "unknown")
    document_type = structure_json.get("file_type", "unknown")
    pages = structure_json.get("pages", [])

    enriched_pages = []

    for page in pages:
        page_number = page.get("page_number", None)
        print(f"\n📄 Enriching page {page_number or '?'}...")

        # Construct page-specific query
        page_text = json.dumps(page, ensure_ascii=False, indent=2)
        query = f"""
        You are an expert in analyzing business and legal documents.
        The following JSON represents one page of extracted structure data.
        For each field and table, do NOT modify names or counts, but enrich with:
        - context_snippet (<=30 words)
        - rag_query (natural-language retrieval query)
        - confidence (0–1)
        Remember for tables there is table label and headers are separate.
        For tables, infer purpose and headers.

        Page structure:
        {page_text}
        """

        # Call LLM for this page
        enriched_data = llm_structured(query, EnrichedDocument)

        if hasattr(enriched_data, "model_dump"):
            enriched_data = enriched_data.model_dump()
        elif hasattr(enriched_data, "dict"):
            enriched_data = enriched_data.dict()

        enriched_page = {
            "page_number": page_number,
            "fields": [
                {
                    "name": f["field_text"],
                    "context": f.get("context_snippet"),
                    "query": f.get("rag_query"),
                    "confidence": f.get("confidence"),
                    "source": None,
                    "value": None
                }
                for f in enriched_data.get("verified_fields", [])
            ],
            "tables": [
                {
                    "name": t.get("table_name"),
                    "context": t.get("context_snippet"),
                    "query": t.get("rag_query"),
                    "confidence": t.get("confidence"),
                    "source": None,
                    "rows": [
                        {col: None for col in t.get("columns", [])}
                    ]
                }
                for t in enriched_data.get("verified_tables", [])
            ]
        }

        enriched_pages.append(enriched_page)

    # Combine into final structure
    enriched_doc = {
        "file_name": file_name,
        "document_type": document_type,
        "pages": enriched_pages
    }

    # # Save to disk
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(enriched_doc, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Enriched structure saved → {output_path}")
    total_fields = sum(len(p["fields"]) for p in enriched_pages)
    total_tables = sum(len(p["tables"]) for p in enriched_pages)
    print(f"   Total pages: {len(enriched_pages)} | Fields: {total_fields} | Tables: {total_tables}")

    return enriched_doc


# ============================================================
# 🧪 Example usage
# ============================================================

if __name__ == "__main__":
    try:
        enrich_structure("structure.json")
    except Exception as e:
        print(f"⚠️ Error: {e}")
