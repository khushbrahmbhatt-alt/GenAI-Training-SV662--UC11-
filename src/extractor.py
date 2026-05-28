import fitz  # PyMuPDF
import os
import base64

def extract_content_from_pdf(file_path: str) -> dict:
    """
    Reads a PDF. If it contains text, it returns the text.
    If it's a scanned image, it returns base64 encoded images of the pages.
    
    Returns:
        dict: {"type": "text", "content": "raw string"} OR 
              {"type": "image", "content": [list of base64 strings]}
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find the file at {file_path}")
        
    try:
        doc = fitz.open(file_path)
        extracted_text = ""
        
        # 1. Try to extract standard text
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            extracted_text += page.get_text("text") + "\n"
            
        clean_text = extracted_text.strip()
        
        # 2. If we found text, return it normally!
        if len(clean_text) > 50: # Using 50 as a safe threshold
            return {"type": "text", "content": clean_text}
            
        # 3. If no text is found, fallback to Vision (Image Extraction)
        base64_images = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Take a high-quality "screenshot" of the page
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) 
            img_bytes = pix.tobytes("png")
            base64_encoded = base64.b64encode(img_bytes).decode("utf-8")
            base64_images.append(base64_encoded)
            
        return {"type": "image", "content": base64_images}
        
    except Exception as e:
        raise RuntimeError(f"An error occurred during extraction: {e}")

# --- Quick Local Test ---
if __name__ == "__main__":
    # Pointing this directly to the file you just tested
    test_file = "/Users/as-mac-0722/Desktop/GenAI-Training-SV662--UC11-/data/Data/Accountant/100.pdf"
    
    if os.path.exists(test_file):
        print(f"Extracting content from {test_file}...\n")
        result = extract_content_from_pdf(test_file)
        
        if result["type"] == "text":
            print(f"✅ Extracted Text: {len(result['content'])} characters.")
            print("-" * 40)
            print(result["content"][:500])
        elif result["type"] == "image":
            print(f"pImage PDF Detected! Converted {len(result['content'])} page(s) to images.")
            print("These images are ready to be sent to gpt-4o-mini's Vision API.")
    else:
        print("Test file not found. Check the path.")