import os
import json
import requests
from dotenv import load_dotenv

# Load .env from sibling folder
dotenv_path = os.path.join(os.path.dirname(__file__), "../JsonGenerator/.env")
load_dotenv(dotenv_path)

API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# Create a board
def create_board(board_name):
    query = f'''
    mutation {{
      create_board (board_name: "{board_name}", board_kind: private) {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()
    if "errors" in json_data:
        print("❌ Error creating board:", json_data["errors"])
        return None
    board_id = json_data["data"]["create_board"]["id"]
    print(f"✅ Board created: {board_name} (ID: {board_id})")
    return board_id

# Create a column (💡 numbers is an enum, no quotes!)
def create_column(board_id, title):
    query = f'''
    mutation {{
      create_column (
        board_id: {board_id},
        title: "{title}",
        column_type: numbers
      ) {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()
    if "errors" in json_data:
        print(f"❌ Error creating column '{title}':", json_data["errors"])
        return None
    column_id = json_data["data"]["create_column"]["id"]
    print(f"✅ Created column: {title} (ID: {column_id})")
    return column_id

# Create a group
def create_group(board_id, group_name):
    query = f'''
    mutation {{
      create_group (board_id: {board_id}, group_name: "{group_name}") {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()
    if "errors" in json_data:
        print(f"❌ Error creating group '{group_name}':", json_data["errors"])
        return None
    return json_data["data"]["create_group"]["id"]

# Create an item with time estimation
def create_item(board_id, group_id, task_name, time_estimation, column_id):
    column_values = {
        column_id: float(time_estimation)
    }
    column_values_json = json.dumps(column_values).replace('"', '\\"')

    query = f'''
    mutation {{
      create_item (
        board_id: {board_id},
        group_id: "{group_id}",
        item_name: "{task_name}",
        column_values: "{column_values_json}"
      ) {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()
    if "errors" in json_data:
        print(f"❌ Error creating item '{task_name}':", json_data["errors"])
    else:
        print(f"✅ Created item: {task_name} ⏱ {time_estimation}")


# Build entire board from JSON structure
def create_full_board(board_name, board_data):
    print(f"🚀 Creating board: {board_name}")
    board_id = create_board(board_name)
    if not board_id:
        print("❌ Failed to create board. Aborting.")
        return

    print(f"🌐 Board URL: https://app.monday.com/boards/{board_id}")

    column_id = create_column(board_id, "Time Estimation")
    if not column_id:
        print("❌ Failed to create column.")
        return

    for group in board_data:
        group_id = create_group(board_id, group["group"])
        if not group_id:
            continue
        for item in group["items"]:
            create_item(
                board_id,
                group_id,
                item["task"],
                item["time_estimation"],
                column_id
            )

    print(f"✅ Done! Board '{board_name}' created successfully.")
