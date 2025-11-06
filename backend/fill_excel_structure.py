import pandas as pd
import json
import os
from noPklRetrieval import rag


def fill_excel_with_rag(extracted_data: dict, input_excel_path: str, output_excel_path: str):
    """
    Takes the extracted fields & tables from extract_excel_data(),
    fills missing fields using RAG, and writes a completed Excel file.
    """
    fields = extracted_data["data"]["fields"]
    tables = extracted_data["data"]["tables"]

    # ✅ Convert field list to DataFrame
    fields_df = pd.DataFrame(fields)
    if "value" not in fields_df.columns:
        fields_df["value"] = None

    # ✅ Fill missing or empty field values using RAG
    for idx, row in fields_df.iterrows():
        if pd.isna(row["value"]) or str(row["value"]).strip().lower() in ["", "n/a", "none"]:
            field_name = row["name"]
            sheet_name = row.get("sheet", "BOV")
            context = f"Sheet: {sheet_name}"
            try:
                filled_value = rag(field_name+" "+context,)
                fields_df.at[idx, "value"] = filled_value
            except Exception as e:
                print(f"⚠️ RAG failed for {field_name}: {e}")

    # ✅ Write results to Excel — each section in its own sheet
    with pd.ExcelWriter(output_excel_path, engine="openpyxl") as writer:
        # Write filled fields
        fields_df.to_excel(writer, sheet_name="Filled Fields", index=False)

        # Write tables if present
        for i, table in enumerate(tables):
            df_table = pd.DataFrame(table["rows"])
            sheet = table.get("name", f"Table_{i+1}")[:31]  # Excel sheet name limit
            df_table.to_excel(writer, sheet_name=sheet, index=False)

    print(f"✅ Final filled Excel written to: {output_excel_path}")



# ---------- Example Run ----------
if __name__ == "__main__":
    # Assuming extract_excel_data() already ran
    from extract_excel_structure import extract_excel_data  # (your previous file)
    
    input_excel_path = "userPdfData/refinalfollowupactionrequiredforyourprototypedeve (1)/BOV Template.xlsx"
    output_excel_path = "filled_BOV_output.xlsx"

    extracted = extract_excel_data(input_excel_path)
    print("extracted ",extracted)
    fill_excel_with_rag(extracted, input_excel_path, output_excel_path)
