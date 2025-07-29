import openai
import fitz  
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)

file_path = os.path.join(os.path.dirname(__file__), "Files", "file.pdf")

pdf_text = extract_text_from_pdf(file_path)
chunk = pdf_text[:4000]  

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
3. For each task, include a `"time_estimation"` field with an estimated time to complete the task in Days. Use realistic, experience-based estimates based on real-world data, typical team velocity, and experience from similar projects. Avoid underestimating or overestimating. The total time should reflect the actual effort required for the PRD, not a fixed target. Each estimate should be between 0.25 and 3 days.
4. Do not include descriptions, explanations, or formatting outside the JSON.
5. Return only a clean JSON structure with this format:

[
  {{
    "group": "General Topic Name",
    "items": [
      {{
        "task": "Short task name",
        "time_estimation": "0.25"
      }},s
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

print(response['choices'][0]['message']['content'])
