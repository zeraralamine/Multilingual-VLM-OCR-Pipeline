import os
import time
import PIL.Image
from google import genai

# Load API key from environment variables
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# The Exception-Routing Prompt
PROMPT = """
You are a highly accurate data extraction assistant building a structured database. 
Read the text in this single column and extract EVERYTHING without skipping a single word.
Output EXACTLY one line per item using this strict 3-part format:
[TAG] | TERM | TRANSLATION / TEXT

=== TAG CLASSIFICATION RULES ===
1. Normal Entry: A standard dictionary term. (Format: [ENTRY] | Term | Translation...)
2. Sub-Entry: Nested variations with no main term. (Format: [SUB-ENTRY] | N/A | [Variation] Text...)
3. Orphaned Text: Text at the VERY TOP of the column continuing from a previous page. (Format: [CONTINUATION] | N/A | Text...)
4. Anomalies: Random symbols or confusing text. (Format: [REVIEW] | N/A | Text...)

=== CRITICAL EXCLUSION ZONE (THE HORIZONTAL LINE RULE) ===
COMPLETELY IGNORE ANY TEXT THAT APPEARS ABOVE THE PRINTED HORIZONTAL LINE AT THE TOP OF THE PAGE. Treat headers, page numbers, and catchwords as INVISIBLE.

=== FORMATTING RULES ===
1. Remove physical line breaks. Stitch text into one continuous paragraph per tag.
2. Transcribe verbatim. Maintain correct Right-to-Left (RTL) grammar, inserting Left-to-Right (LTR) words in their exact proper place.
"""

def extract_text_pipeline(image_folder, output_file):
    """
    Extracts text using Gemini VLM with Exception Routing and Exponential Backoff.
    """
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith(".png")])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Tag|Term|Text\n") # CSV Header
        
        for index, img_file in enumerate(image_files):
            print(f"Scanning {img_file}...")
            success = False
            wait_time = 30
            
            # Exponential Backoff Loop for API Rate Limiting
            for attempt in range(5):
                try:
                    img_path = os.path.join(image_folder, img_file)
                    img = PIL.Image.open(img_path)
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[PROMPT, img]
                    )
                    
                    f.write(response.text.strip() + "\n")
                    success = True
                    break
                    
                except Exception as e:
                    print(f"  -> API Rate Limit. Sleeping {wait_time}s... (Attempt {attempt+1})")
                    time.sleep(wait_time)
                    wait_time += 30 
                    
            if not success:
                f.write(f"[ERROR] | N/A | FAILED TO EXTRACT {img_file}\n")
            
            time.sleep(5) # Standard API cooldown

if __name__ == "__main__":
    extract_text_pipeline('./data/2_columns', './data/3_output/master_transcript.txt')
