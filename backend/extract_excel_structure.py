import pandas as pd
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from llm import llm_structured
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional

class ExcelField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Field name, e.g. 'Tenant', 'Address', 'Annual Rent'.")
    value: Optional[str] = None
    sheet: Optional[str] = None
    cell: Optional[str] = None
    # confidence: Optional[float] = None
    # source: Optional[List[str]] = Field(default_factory=list)
    # reason: Optional[str] = None
    query: str = Field(..., description="""The query, keywords, or sentence used to retrieve this table’s data should be designed for similarity search. Identify whether it’s a direct query (e.g., specific terms like “Annual Rent”, which do not require expansion) or an indirect/conceptual query (e.g., “Weakness”, where the meaning is broader and requires expansion into related terms or phrases).

For indirect queries, ensure the search terms are expanded, rephrased, or translated into related concepts that can retrieve useful information from leadership or reference documents — content that helps in writing sections like “Weakness.”

In short, determine whether the query needs semantic expansion or can remain literal, based on how the data is represented in source documents.""")

class ExcelTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Table name or title.")
    sheet: Optional[str] = None
    headers: Optional[List[str]] = Field(default_factory=list)
    rows: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    # confidence: Optional[float] = None
    # source: Optional[List[str]] = Field(default_factory=list)
    # reason: Optional[str] = None
    query: str = Field(..., description= """The query, keywords, or sentence used to retrieve this table’s data should be designed for similarity search. Identify whether it’s a direct query (e.g., specific terms like “Annual Rent”, which do not require expansion) or an indirect/conceptual query (e.g., “Weakness”, where the meaning is broader and requires expansion into related terms or phrases).

For indirect queries, ensure the search terms are expanded, rephrased, or translated into related concepts that can retrieve useful information from leadership or reference documents — content that helps in writing sections like “Weakness.”

In short, determine whether the query needs semantic expansion or can remain literal, based on how the data is represented in source documents.""")

class ExcelChunkExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fields: Optional[List[ExcelField]] = Field(default_factory=list)
    tables: Optional[List[ExcelTable]] = Field(default_factory=list)


# ---------- Step 2: LangChain Structured Output Helper ----------
# def llm_structured(prompt: str, response_model):
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).with_structured_output(
#         schema=response_model,
#         method="function_calling"  # ✅ required for langchain-openai >= 0.3
#     )
#     return llm.invoke([HumanMessage(content=prompt)])


# ---------- Step 3: Chunking ----------
def chunk_dataframe(df: pd.DataFrame, max_rows: int = 40):
    """
    Breaks large DataFrames into smaller chunks while keeping row continuity.
    """
    chunks = []
    for start in range(0, len(df), max_rows):
        chunk = df.iloc[start:start + max_rows]
        chunks.append(chunk)
    return chunks


# ---------- Step 4: Extraction Logic ----------
def extract_excel_data(excel_path: str):
    all_fields, all_tables = [], []

    # for sheet_name in excel_data.sheet_names:
    for sheet_name in ['BOV']:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        chunks = chunk_dataframe(df)

        for i, chunk in enumerate(chunks):
            csv_view = chunk.to_csv(index=False,header=False)
            print("csv view ", csv_view)
            prompt = f"""
You are an expert at extracting structured information from Excel sheets.
The data belons to lease documents and forms of it.
The data below is from the sheet **"{sheet_name}"**, chunk {i+1}/{len(chunks)}.

Extract and return:
1. Key **fields** (like Tenant, Address, Annual Rent, etc.)
2. Any **tables** (like Rent Schedule, Strengths, Weaknesses, etc.)

⚙️ OUTPUT INSTRUCTIONS:
- Each field should include: name, value, sheet, cell (if possible), confidence, source, and reason.
- Each table should include: name, sheet, headers, rows, confidence, source, and reason.
- Only include fields/tables that seem meaningful and have actual values (ignore placeholders or headers).

Data:
{csv_view}

Now extract structured data in the required schema.
"""

            try:
                result = llm_structured(prompt, ExcelChunkExtraction)
                print("result ", result)
                if result:
                    all_fields.extend(result.fields)
                    all_tables.extend(result.tables)
            except Exception as e:
                print(f"⚠️ Error processing {sheet_name}[{i}]: {e}")
                continue

    return {"data": {"fields": [f.model_dump() for f in all_fields],
                     "tables": [t.model_dump() for t in all_tables]}}, csv_view


# ---------- Step 5: Example Run ----------
if __name__ == "__main__":
    excel_path = "userPdfData/refinalfollowupactionrequiredforyourprototypedeve (1)/BOV Template.xlsx"  # Replace with your file path
    result,csv_view = extract_excel_data(excel_path)
    

    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("CSV View of last chunk:\n", csv_view)
    with open("extracted_excel_structure.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)