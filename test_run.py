import os
import json
from src.extractor import extract_content_from_pdf
from src.engine import analyze_resume

def main():
    # Setup your test variables
    # (Using the exact file path that just worked for you)
    test_pdf = "/Users/as-mac-0722/Desktop/GenAI-Training-SV662--UC11-/data/Data/Accountant/100.pdf"
    target_role = "Accountant"
    file_name = os.path.basename(test_pdf)

    print(f"Step 1: Reading {file_name}...")
    extracted_data = extract_content_from_pdf(test_pdf)
    print(f"-> Detected type: {extracted_data['type']}")

    print("\nStep 2: Sending to gpt-4o-mini...")
    # This might take 5-15 seconds depending on your internet and OpenAI's API speed
    final_output = analyze_resume(
        extracted_data=extracted_data, 
        target_role=target_role, 
        file_name=file_name
    )

    print("\nStep 3: Success! Here is the validated JSON:")
    # We use .model_dump_json(indent=2) to print the Pydantic object beautifully
    print(final_output.model_dump_json(indent=2))

if __name__ == "__main__":
    main()