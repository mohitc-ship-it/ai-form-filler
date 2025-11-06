from fill_structure import fill_docx_using_enriched
from get_structure import extract_structure
from extract_excel_structure import extract_excel_data
from enrich_structure import enrich_structure
from fillData import run_excel_filling_pipeline


from pathlib import Path

from ragAnything import store_document, query_rag
from utils import parse_csv_to_json, convert_model_output_to_final_format, checkDbs

def checkDbAvaialbility():
    pass

async def fill_excel(file_input,session_id):
    """
    Given an Excel file input, extract its structure,
    fill it with data, and return the filled structure.
    """
    structure,csv_updated = extract_excel_data(file_input)
    print(type(structure))
    # structure= json.loads(structure)
    file_path,fill_csv = await run_excel_filling_pipeline(file_input,structure,csv_updated)
    print("filled csv is ", fill_csv)
    final_csv_json = parse_csv_to_json(fill_csv)
    return final_csv_json

async def fill_docx(file_input,session_id):
    """
    Given a DOCX file input, extract its structure,
    fill it with data, and return the filled structure.
    """
    print("filling docx now")
    structure = extract_structure(file_input)
    enriched_structure = enrich_structure(structure)
    filled_data_object = await fill_docx_using_enriched(file_input,enriched_structure)
    final_json = convert_model_output_to_final_format(filled_data_object['data'])
    return final_json


# fill_excel("userPdfData/refinalfollowupactionrequiredforyourprototypedeve (1)/BOV Template.xlsx")
# fill_docx("Lease Abstract Template.docx")
# template_path: str, enriched_json_path: str, output_path: str = None



# def reqHandler(session_id: str,user_files:any):
#     """
#     Explore both 'forms' and 'context' folders inside a session directory,
#     and return all file paths as a list.
#     """

#     uploadDir = Path("uploaded_files/")  # root directory where sessions are stored
#     userDataPath = os.path.join(uploadDir , session_id)
#     contextPath = userDataPath + "/context/"
#     formPath = userDataPath + "/forms/"

#     for context_file in os.listdir(contextPath):
#         store_document(os.path.join(contextPath,context_file))
    
#     for form_file in os.listdir(formPath):
#         # result = query_rag(os.path.join(formPath,form_file))
#         if(form_file.lower().endswith(".docx")):
#             result = fill_docx(os.path.join(formPath,form_file),session_id)
#         elif(form_file.lower().endswith(".xlsx")):
#             result = fill_excel(os.path.join(formPath,form_file),session_id)
    
#     return result
    
async def reqHandler(session_id: str, user_files: any):
    uploadDir = Path("uploaded_files")
    
    # Try to auto-detect full folder name that contains session_id
    matching_dirs = [p for p in uploadDir.iterdir() if session_id in p.name]
    if not matching_dirs:
        print(f"⚠️ No folder found containing session ID {session_id}")
        return "file_not_found"

    userDataPath = matching_dirs[0]
    contextPath = userDataPath / "context"
    formPath = userDataPath / "forms"

    print(f"✅ Using session directory: {userDataPath}")

    results = []

    # --- Process context files ---
    if contextPath.exists():
        for context_file in contextPath.iterdir():
            if context_file.is_file() and not checkDbs(context_file.name):
                print(f"🧠 Storing context file: {context_file.name}")
                await store_document(context_file)
    else:
        print(f"⚠️ Context folder missing: {contextPath}")
        return "file_not_found"

    # --- Process form files ---
    if formPath.exists():
        for form_file in formPath.iterdir():
            if not form_file.is_file():
                continue
            res = None
            if form_file.suffix.lower() == ".docx":
                print(f"📄 Processing DOCX form: {form_file.name}")
                res = await fill_docx(form_file, session_id)
            elif form_file.suffix.lower() == ".xlsx":
                print(f"📊 Processing XLSX form: {form_file.name}")
                res = await fill_excel(form_file, session_id)
            results.append({
                "file": form_file.name,
                "path": str(form_file),
                "result": res
            })
    else:
        print(f"⚠️ Forms folder missing: {formPath}")

    return results
