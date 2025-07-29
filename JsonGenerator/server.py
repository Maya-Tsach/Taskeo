import openai
import fitz  # PyMuPDF for reading PDFs
import os
from dotenv import load_dotenv

# Load .env and set API key
load_dotenv()
openai.api_key = os.getenv("API_KEY")

# Extract text from PRD PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

# PDF input
file_path = "/Users/sharons/Desktop/PRD-EventFlow .pdf"
pdf_text = extract_text_from_pdf(file_path)
chunk = pdf_text[:4000]  # Trim for token limits if needed

# Prompt GPT to generate board-style JSON
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are an expert product analyst. Your job is to extract board-style project planning data from PRDs and return it in JSON format for Monday-style task boards."
        },
        {
            "role": "user",
            "content": f"""Here is a PRD document. Please identify the main product areas (groups) and list the initial tasks (items) needed for each.
For each item, return the following fields: item name, short description, person (if known), status, priority, sprint, time estimation (in hours), timeline (start–end), actual timeline (if known).
Return JSON in this format:

[
  {{
    "group": "Home Page",
    "items": [
      {{
        "item": "Header",
        "description": "Build top navigation bar with logo and menu",
      }},
      ...
    ]
  }},
  ...
]

Now extract from this PRD:
{chunk}
"""
        }
    ]
)

# Output result
print(response['choices'][0]['message']['content'])
