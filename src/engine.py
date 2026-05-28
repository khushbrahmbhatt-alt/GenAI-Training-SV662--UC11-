import os
import json
import requests
from dotenv import load_dotenv
from src.schema import ResumeExtractionSchema

# Load environmental variables
load_dotenv()

def analyze_resume(extracted_data: dict, target_role: str, file_name: str) -> ResumeExtractionSchema:
    """
    Processes resume data (text or image) using direct HTTP requests to Azure OpenAI
    and parses the output into the validated Pydantic schema.
    """
    # Grab configuration from environment
    # Grab configuration and strictly strip out any accidental spaces or quotes
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().strip('"').strip("'")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip().strip('"').strip("'")
    deployment = os.getenv("DEPLOYMENT_NAME", "").strip().strip('"').strip("'")
    api_version = os.getenv("API_VERSION", "").strip().strip('"').strip("'")
    
    # Construct the exact URL matching your working snippet
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    
    # System instructions defining what to pull and evaluate
    system_instruction = (
        "You are an advanced AI Applicant Tracking System (ATS) optimization engine. "
        "Analyze the provided resume and output a raw JSON object that strictly matches this Pydantic schema structural layout:\n\n"
        f"{json.dumps(ResumeExtractionSchema.model_json_schema(), indent=2)}\n\n"
        "Strict Requirements:\n"
        "1. Do not include markdown code block styling like ```json ... ``` in your response. Output raw JSON prose only.\n"
        f"2. Fulfill Part 1 (Extraction) and Part 2 (Analysis scoring against target role: {target_role}).\n"
        "3. Do not hallucinate empty fields; use null or an empty list if data is missing."
    )
    
    # Build user message content depending on text or image structure
    if extracted_data["type"] == "text":
        user_content = [
            {"type": "text", "text": f"Target Role: {target_role}\nFile Name: {file_name}\n\nResume Text:\n{extracted_data['content']}"}
        ]
    elif extracted_data["type"] == "image":
        user_content = [
            {"type": "text", "text": f"Target Role: {target_role}\nFile Name: {file_name}\n\nPlease extract and analyze the attached resume image pages."}
        ]
        for base64_image in extracted_data["content"]:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
            })
    else:
        raise ValueError("Invalid extracted_data type. Must be 'text' or 'image'.")

    # Final Payload matching your request format structure
    payload = {
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"}  # Forces the model to respond in valid JSON
    }
    
    try:
        # Fire the POST request exactly like your script snippet
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        raw_json_string = response_data["choices"][0]["message"]["content"].strip()
        
        # Parse and validate the raw text output straight into our target Pydantic object
        validated_output = ResumeExtractionSchema.model_validate_json(raw_json_string)
        return validated_output
        
    except Exception as e:
        if 'response' in locals() and response is not None:
            raise RuntimeError(f"API Execution Failed (Status {response.status_code}): {response.text}")
        raise RuntimeError(f"Direct Azure connection step failed: {e}")