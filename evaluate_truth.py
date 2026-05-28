import os
import pandas as pd
import time
import difflib
from src.extractor import extract_content_from_pdf
from src.engine import analyze_resume

# --- HELPER FUNCTIONS ---

def get_section_text(df, section_name: str) -> str:
    try:
        mask = df[0].astype(str).str.strip().str.lower() == section_name.lower()
        if mask.any():
            return str(df[mask].iloc[0, 1]).strip()
    except Exception:
        pass
    return ""

def extract_from_text_block(block: str, key: str) -> str:
    if pd.isna(block) or not block:
        return ""
    for line in str(block).split('\n'):
        if line.lower().startswith(key.lower()):
            if ':' in line:
                return line.split(':', 1)[1].strip()
    return ""

def compare_strings_fuzzy(ai_value, truth_value, threshold=0.75) -> int:
    if not ai_value and not truth_value: return 1
    if not ai_value or not truth_value: return 0
    ai_str = str(ai_value).strip().lower()
    truth_str = str(truth_value).strip().lower()
    if ai_str in truth_str or truth_str in ai_str: return 1
    similarity_score = difflib.SequenceMatcher(None, ai_str, truth_str).ratio()
    return 1 if similarity_score >= threshold else 0

def compare_list_to_block_fuzzy(ai_list, truth_block: str, threshold=0.60) -> int:
    if not ai_list and not truth_block: return 1
    if not ai_list or not truth_block: return 0
    truth_lower = str(truth_block).lower()
    matched_items = 0
    for item in ai_list:
        item_str = str(item).lower()
        if item_str in truth_lower:
            matched_items += 1
        else:
            for word in truth_lower.split():
                if difflib.SequenceMatcher(None, item_str, word).ratio() > 0.8:
                    matched_items += 1
                    break 
    pass_ratio = matched_items / len(ai_list)
    return 1 if pass_ratio >= threshold else 0

def find_pdf_in_directory(base_dir: str, target_filename: str) -> str:
    for root, dirs, files in os.walk(base_dir):
        if target_filename in files:
            return os.path.join(root, target_filename)
    return None

# --- MAIN EVALUATION PIPELINE ---

def run_evaluation(excel_file: str, base_pdf_folder: str, output_excel: str):
    print(f"Loading Ground Truth Excel File: {excel_file}\n")
    xls = pd.ExcelFile(excel_file)
    results = []
    
    for sheet_name in xls.sheet_names:
        print(f"--- Evaluating Tab: {sheet_name} ---")
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        
        try:
            pdf_filename = str(df.iloc[1, 1]).strip() 
            target_role = str(df.iloc[2, 1]).strip()  
            
            truth_personal = get_section_text(df, 'Personal Details')
            truth_contact = get_section_text(df, 'Contact Information')
            truth_summary = get_section_text(df, 'Professional Summary')
            truth_experience = get_section_text(df, 'Work Experience')
            truth_education = get_section_text(df, 'Education')
            truth_skills = get_section_text(df, 'Skills')
            truth_languages = get_section_text(df, 'Languages')
            truth_derived = get_section_text(df, 'Derived Insights') 
            truth_ats = get_section_text(df, 'ATS Scoring')          
            
            truth_name = extract_from_text_block(truth_personal, "Full Name")
            truth_email = extract_from_text_block(truth_contact, "Email")
            truth_exp_years = extract_from_text_block(truth_derived, "Total Experience")
            truth_score = extract_from_text_block(truth_ats, "Profile Score")
            
        except Exception as e:
            print(f"   ⚠️ Could not parse sheet structure. Error: {e}")
            continue

        file_path = find_pdf_in_directory(base_pdf_folder, pdf_filename)
        
        if not file_path:
            print(f"   ⚠️ WARNING: Could not find '{pdf_filename}'. Skipping.")
            continue
            
        try:
            print(f"   Processing AI Extraction...")
            extracted_data = extract_content_from_pdf(file_path)
            ai_output = analyze_resume(extracted_data, target_role, pdf_filename)
            
            ai_companies = [job.company_name for job in ai_output.work_experience if job.company_name]
            ai_schools = [edu.institution for edu in ai_output.education if edu.institution]
            
            scores = {
                "Name": compare_strings_fuzzy(ai_output.personal_details.full_name, truth_name),
                "Email": compare_strings_fuzzy(ai_output.contact_information.email, truth_email),
                "Summary": compare_strings_fuzzy(ai_output.professional_summary, truth_summary),
                "Skills": compare_list_to_block_fuzzy(ai_output.skills, truth_skills),
                "Languages": compare_list_to_block_fuzzy(ai_output.languages, truth_languages),
                "Experience": compare_list_to_block_fuzzy(ai_companies, truth_experience),
                "Education": compare_list_to_block_fuzzy(ai_schools, truth_education),
                "Total Exp Yrs": compare_strings_fuzzy(ai_output.derived_insights.total_experience_years, truth_exp_years),
                "ATS Score Match": compare_strings_fuzzy(ai_output.ats_scoring.profile_score, truth_score)
            }

            accuracy_score = (sum(scores.values()) / len(scores)) * 100
            
            # Pure Side-by-Side Formatting + Final Score
            row_data = {
                "File Name": pdf_filename,
                "Target Role": target_role,
                
                "Truth Name": truth_name,
                "AI Name": ai_output.personal_details.full_name,
                
                "Truth Email": truth_email,
                "AI Email": ai_output.contact_information.email,
                
                "Truth Summary": truth_summary[:100] + "..." if truth_summary else "",
                "AI Summary": ai_output.professional_summary[:100] + "..." if ai_output.professional_summary else "",
                
                "Truth Skills": truth_skills,
                "AI Skills": ", ".join(ai_output.skills) if ai_output.skills else "",
                
                "Truth Languages": truth_languages,
                "AI Languages": ", ".join(ai_output.languages) if ai_output.languages else "",
                
                "Truth Experience": truth_experience[:100] + "..." if truth_experience else "",
                "AI Experience (Companies)": ", ".join(ai_companies),
                
                "Truth Education": truth_education[:100] + "..." if truth_education else "",
                "AI Education": ", ".join(ai_schools),
                
                "Truth Exp Yrs": truth_exp_years,
                "AI Exp Yrs": ai_output.derived_insights.total_experience_years,
                
                "Truth ATS Score": truth_score,
                "AI ATS Score": ai_output.ats_scoring.profile_score,
                
                "RESUME ACCURACY SCORE %": round(accuracy_score, 1)
            }
                
            results.append(row_data)
            print(f"   ✅ Score: {accuracy_score:.1f}%\n")
            time.sleep(2) 
            
        except Exception as e:
            print(f"   ❌ Failed to process {pdf_filename}: {e}\n")

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_excel(output_excel, index=False)
        print(f"Saved Side-by-Side Evaluation to: {output_excel}")

if __name__ == "__main__":
    EXCEL_FILE = "/Users/as-mac-0722/Desktop/GenAI-Training-SV662--UC11-/data/Data/Ground_Truth.xlsx" 
    BASE_PDF_FOLDER_PATH = "/Users/as-mac-0722/Desktop/GenAI-Training-SV662--UC11-/data/Data"
    OUTPUT_EVAL_FILE = "GroundTruth_Evaluation.xlsx"
    
    run_evaluation(EXCEL_FILE, BASE_PDF_FOLDER_PATH, OUTPUT_EVAL_FILE)