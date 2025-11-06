import csv
import io
import json
from typing import List, Dict, Any

def parse_csv_to_json(csv_text: str) -> List[Dict[str, Any]]:
    """
    Convert messy CSV-like lease abstract input into structured JSON.

    Handles:
      - Regular key-value lines like: ",Tenant,FIRST NATIONAL BANK,,,,"
      - Table sections (e.g. 'Rent Schedule')
      - Blank / comment lines (ignored)
    """
    print("parsing csv to json")
    lines = [line.strip() for line in csv_text.splitlines() if line.strip() and not line.strip().startswith("#")]
    records = []
    current_table = None
    headers = []
    rows = []
    
    for line in lines:
        # Clean up commas and split CSV-style
        parts = [p.strip() for p in next(csv.reader(io.StringIO(line))) if p.strip()]
        if not parts:
            continue
        
        # Detect section/table start
        if len(parts) == 1 and not parts[0].isdigit():
            # Save any previous table before starting a new one
            if current_table and headers and rows:
                records.append({
                    "type": "table",
                    "title": current_table,
                    "data": {
                        "headers": headers,
                        "rows": rows
                    },
                    "explanation": "",
                    "source": ""
                })
                headers, rows = [], []

            current_table = parts[0]
            continue

        # If inside a table section
        if current_table and len(parts) > 2:
            if not headers:
                headers = parts  # first non-title row = header row
            else:
                rows.append(parts)
            continue

        # Regular key-value fields (non-table)
        if len(parts) >= 2:
            field = parts[0]
            value = parts[1]
            records.append({
                "field": field,
                "value": value,
                "explanation": "",
                "source": ""
            })

    # Append final table if one remains
    if current_table and headers and rows:
        records.append({
            "type": "table",
            "title": current_table,
            "data": {
                "headers": headers,
                "rows": rows
            },
            "explanation": "",
            "source": ""
        })

    return records


# ============================
# Example usage
# ============================
# if __name__ == "__main__":
#     raw_csv = """
#     ,,,,,,,,,,,,2024-09-30
#     ,Investment Summary,,,,,,,,,,,
#     ,Address,Magnolia Road and 9th Street,,,,,,,,,,,
#     ,"City, State",,,,,,,,,,,,
#     ,Tenant,FIRST NATIONAL BANK AND TRUST COMPANY,,,,,,,,,,,
#     ,Annual Rent,$7,000,,,,,,,,,,,
#     ,Lease Expiration,July 31, 2033,,,,,,,,,,,
#     ,Term Remaining,0 years,,,,,,,,,,,
#     ,Building Square Footage,249,861.70 sq. ft.,,,,,,,,,,,,
#     ,Parcel Size (AC),0.67 acres,,,,,,,,,,,
#     ,Lease Type,Commercial Lease,,,,,,,,,,,
#     ,Landlord Responsibilities,1. Maintenance...,,,,,,,,,,,
#     ,Branch Deposits,,,,,,,,,,,
#     ,,,,,,,,,,,,
#     ,Rent Schedule,,,,,,,,,,,
#     Tenant,Square Feet,Commencement Date,Expiration Date,Step Up Date ,Rent,,,,,,,
#     ,SUNFLOWER BANK,11,174.17,August 1 2023,July 31 2033,$22.00 PSF,,,,,
#     ,SUNFLOWER BANK,12,190.00,August 1 2028,July 31 2033,$24.00 PSF,,,,,
#     ,,,,,,,,,,,,
#     ,Strengths,,,,,,,,,,,
#     ,,,,,,,,,,,,
#     ,Weaknesses,,,,,,,,,,,
#     """

#     result = parse_csv_to_json(raw_csv)
#     print(json.dumps(result, indent=2))

import json
from typing import List, Dict, Any, Union

def convert_model_output_to_final_format(model_output: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converts model-extracted 'fields' and 'tables' JSON output into the standardized
    final JSON schema used for summary and Excel-style data ingestion.
    """

    final_output = []

    # ---- Handle Fields ----
    for field in model_output.get("fields", []):
        name = field.get("name")
        value = field.get("value")
        reason = field.get("reason")
        source = field.get("source")

        # Handle cases where source is list → join nicely
        if isinstance(source, list):
            source_str = " and ".join(source) if len(source) <= 2 else ", ".join(source)
        else:
            source_str = source or ""

        final_output.append({
            "field": name,
            "value": value,
            "explanation": reason or "",
            "source": source_str
        })

    # ---- Handle Tables ----
    for table in model_output.get("tables", []):
        table_title = table.get("name", "Table")
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        source = table.get("source", "")
        confidence = table.get("confidence")
        explanation = f"Data extracted from {table_title} section of lease documents."

        # Create structured table format
        table_obj = {
            "type": "table",
            "title": "Rent Schedule" if "rent" in table_title.lower() else table_title,
            "data": {
                "headers": headers,
                "rows": rows
            },
            "explanation": explanation,
            "source": source
        }

        final_output.append(table_obj)

    return final_output


# # -------- Example Usage --------
# if __name__ == "__main__":
#     with open("model_output.json", "r") as f:
#         model_output = json.load(f)

#     final_data = convert_model_output_to_final_format(model_output)
#     print(json.dumps(final_data, indent=2, ensure_ascii=False))



import os
def checkDbs(db_name: str) -> bool:
    """
    Check if the specified database exists in the working directory.
    """
    from ragAnything import OUTPUT_ROOT
    # db_path = os.path.join(OUTPUT_ROOT, db_name)
    available_dbs = [d for d in os.listdir(OUTPUT_ROOT) if os.path.isdir(os.path.join(OUTPUT_ROOT, d))]
    db_name = db_name.split(".")[0]
    for db in available_dbs:
        
        print("current db is ", db)
        print("checking for ", db_name)
        if db_name in db:
            return True
    return False