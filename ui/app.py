import streamlit as st
import os
import tempfile
import sys
import json

# Add the root directory to the system path so it can find the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.extractor import extract_content_from_pdf
from src.engine import analyze_resume

# Set up the page layout
st.set_page_config(page_title="AI Resume Parser (ATS)", layout="wide")

st.title("📄 AI-Powered Applicant Tracking System")
st.markdown("Upload a candidate's resume (Text or Scanned PDF) to extract data and evaluate their fit for a specific role.")

# Create a two-column layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Upload & Configure")
    target_role = st.text_input("Target Role (e.g., Accountant, Architect):", value="Accountant")
    uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])
    
    analyze_button = st.button("Analyze Resume", type="primary", use_container_width=True)

with col2:
    st.header("2. Analysis Results")
    
    if analyze_button and uploaded_file is not None and target_role:
        with st.spinner("Extracting document content and analyzing via Azure OpenAI..."):
            try:
                # 1. Save the uploaded file temporarily so PyMuPDF can read it
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_pdf_path = tmp_file.name

                # 2. Extract Text or Image
                extracted_data = extract_content_from_pdf(temp_pdf_path)
                
                # 3. Analyze using the AI Engine
                result = analyze_resume(extracted_data, target_role, uploaded_file.name)
                
                # Clean up the temp file
                os.remove(temp_pdf_path)

                # --- UI DISPLAY ---
                st.success("Analysis Complete!")
                
                # Display Top-Level Metrics
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                metrics_col1.metric("ATS Profile Score", f"{result.ats_scoring.profile_score * 100:.0f}%")
                metrics_col2.metric("Total Experience", f"{result.derived_insights.total_experience_years} Yrs")
                metrics_col3.metric("Management Exp", "Yes" if result.derived_insights.management_experience else "No")
                
                # Display Confidence Factors
                st.subheader(f"Why {result.personal_details.full_name} scored {result.ats_scoring.profile_score * 100:.0f}% for '{target_role}'")
                for factor in result.ats_scoring.confidence_factors:
                    st.markdown(f"- {factor}")
                
                st.divider()
                
                # Display the raw JSON payload in a nice expander
                with st.expander("View Raw Extracted JSON"):
                    st.json(result.model_dump())

            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                
    elif analyze_button:
        st.warning("Please upload a PDF and specify a target role first.")