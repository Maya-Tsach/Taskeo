import json
from JsonGenerator.groupsGenerator import generate_groups_from_pdf
from mondayCreation.boardCreation import create_full_board

def main():
    # Step 1: Generate structured board data from PDF
    print("🔍 Extracting project structure from PRD...")
    raw_response = generate_groups_from_pdf()
    
    # Print the raw response for debugging
    print("\n🛠️ Raw Response from OpenAI:\n")
    print(raw_response)

    # Attempt to parse the response as JSON
    try:
        board_data = json.loads(raw_response)
    except json.JSONDecodeError as e:
        print(f"\n❌ Failed to decode JSON: {e}")
        return

    print("\n📄 Generated Board Data:\n")
    print(json.dumps(board_data, indent=2))

    # Step 2: Create Monday.com board
    print("\n🧱 Creating board on Monday.com...")
    create_full_board("PRD Project Board", board_data)

if __name__ == "__main__":
    main()
