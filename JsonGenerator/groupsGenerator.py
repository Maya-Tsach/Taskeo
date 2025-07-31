import openai
import fitz  # PyMuPDF
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")

def split_text(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def generate_groups_from_pdf(file_stream):
    doc = fitz.open(stream=file_stream.read(), filetype="pdf")
    pdf_text = "\n".join(page.get_text() for page in doc)

    chunks = split_text(pdf_text, 4000)
    all_groups = []

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx+1}/{len(chunks)}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a product analyst assistant. You help turn PRDs into structured boards for development planning."
                },
                {
                    "role": "user",
                    "content": f"""
                      You are a product analyst assistant. Your task is to extract a structured project board from the following PRD.
                      Follow these instructions carefully:
                      1. Organize features into *general, high-level groups* that represent broad product areas or workflows. Avoid using specific feature names (e.g. “Login Button”) as group titles — use broader categories like “Authentication” or “User Dashboard”.
                      2. Each group must contain a list of **short task names** (2–5 words).
                      3. For **each task**, you must include a key named `"time_estimation_AI"` (exact spelling) with an estimated time in days. Valid values: `"0.25"`, `"0.5"`, `"1"`, `"2"`, etc. ⚠️ Do not use `"time_estimation"` or any other variation.
                      4. **Return ONLY JSON** — no comments, markdown, or extra explanations.
                      5. Ignore any PRD sections that do not relate to developer/designer implementation tasks (e.g. Overview, Goals, Terminology, System Specs).
                      6. The output **must** exactly match this format:

                      [
                        {{
                          "group": "General Topic Name",
                          "items": [
                            {{
                              "task": "Short task name",
                              "time_estimation_AI": "0.25"
                            }},
                            ...
                          ]
                        }},
                        ...
                      ]

                      Here is the PRD:
                      ---
                      {chunk}
                      ---
                      """
                }
            ]
        )
        raw_content = response['choices'][0]['message']['content']
        cleaned_json = re.sub(r"^```json|```$", "", raw_content.strip(), flags=re.MULTILINE)
        try:
            groups = json.loads(cleaned_json)
            all_groups.extend(groups)
        except Exception as e:
            print(f"Error parsing chunk {idx+1}: {e}")

    # Filter out empty groups (no 'group' or no 'items')
    all_groups = [
        g for g in all_groups
        if isinstance(g, dict) and g.get("group") and g.get("items")
    ]

    print("PRD converted to board structure")
    return json.dumps(all_groups)
