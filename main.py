from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from JsonGenerator.groupsGenerator import generate_groups_from_pdf
from mondayCreation.boardCreation import create_full_board
import json

app = FastAPI()

# CORS setup – allow frontend connection (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ In production, replace "*" with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-board/")
async def generate_board(
    file: UploadFile = File(...),
    board_name: str = Form(...),
    monday_api_key: str = Form(...)
):
    # Step 1: Extract structured tasks from PDF
    try:
        print("Extracting project structure from PRD...")
        raw_response = generate_groups_from_pdf(file.file)  # or use BytesIO(await file.read())
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Failed to parse PDF: {str(e)}"})

    print("Raw Response from OpenAI:")
    print(raw_response)

    # Step 2: Parse OpenAI output into board structure
    try:
        board_data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        return JSONResponse(status_code=400, content={"error": f"Invalid JSON: {str(e)}"})

    print("Creating board on Monday.com...")

    # Step 3: Define additional columns
    extra_columns = [
        {"title": "Person", "type": "people"},
        {"title": "Status", "type": "status"},
        {
            "title": "Priority",
            "type": "status",
            "description": "This column indicates the urgency level",
            "labels": {
                "0": "Critical",
                "1": "High",
                "2": "Medium",
                "3": "Low"
            }
        },
        {"title": "Sprint", "type": "text"},
        {"title": "Timeline", "type": "timeline"},
        {"title": "Actual Time", "type": "numbers"},
        {"title": "Actual Timeline", "type": "timeline"}
    ]

    # Step 4: Create the Monday board
    try:
        create_full_board(board_name, board_data, extra_columns, api_key=monday_api_key)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Board creation failed: {str(e)}"})

    return {"message": f"Board '{board_name}' created successfully!"}
