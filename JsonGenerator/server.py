import openai
import fitz  # PyMuPDF for reading PDFs
import os
from dotenv import load_dotenv

# Load .env file and get the API key
load_dotenv()
openai.api_key = os.getenv("API_KEY")

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

# Set the file path to the PRD PDF
file_path = os.path.join(os.path.dirname(__file__), "Files", "file.pdf")

# Read and optionally trim the PDF text for context length
pdf_text = extract_text_from_pdf(file_path)
chunk = pdf_text[:4000]  # GPT-3.5-turbo max context is ~4096 tokens

# Use OpenAI to convert PRD into JSON of groups and items
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

Please follow these rules:

1. Organize features into **general, high-level groups** that represent broad product domains, workflows, or modules. Avoid using specific feature names as group titles.
2. Each group should contain a list of **short task titles** (2-5 words), representing key items or subtasks relevant to that group.
3. Do not include descriptions, explanations, or formatting outside the JSON.
4. Return only a clean JSON structure with this format:

[
  {{
    "group": "General Topic Name",
    "items": [
      "Short task name",
      "Short task name",
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

# Output the structured board-style JSON
print(response['choices'][0]['message']['content'])
