import json
from JsonGenerator.groupsGenerator import generate_groups_from_pdf
from mondayCreation.boardCreation import create_full_board

def main():
    boardName = "PRD Project Board"

    print(" Extracting project structure from PRD")
    raw_response = generate_groups_from_pdf()
    
    print("\n Raw Response from OpenAI:\n")
    print(raw_response)

    try:
        board_data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"\n Failed to decode JSON: {e}")
        return

    print("\n Generated Board Data:\n")
    print(json.dumps(board_data, indent=2))

    print("\n Creating board on Monday")
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

    create_full_board(boardName, board_data, extra_columns)

if __name__ == "__main__":
    main()
