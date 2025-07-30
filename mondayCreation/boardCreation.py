import os
import json
import requests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)

API_KEY = os.getenv("MONDAY_API_KEY")
API_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

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
        print("Error creating board:", json_data["errors"])
        return None
    board_id = json_data["data"]["create_board"]["id"]
    print(f"Board created: {board_name} (ID: {board_id})")
    return board_id

def create_column(board_id, title, column_type="numbers", defaults=None, description=None):
    defaults_part = f', defaults: "{defaults}"' if defaults else ""
    description_part = f', description: "{description}"' if description else ""

    query = f'''
    mutation {{
      create_column (
        board_id: {board_id},
        title: "{title}",
        column_type: {column_type}
        {description_part}
        {defaults_part}
      ) {{
        id
      }}
    }}
    '''
    print(f"\n📤 Creating column: {title}")
    print(query)

    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()

    print("📥 API Response:")
    print(json.dumps(json_data, indent=2))

    if "errors" in json_data:
        print(f"❌ Error creating column '{title}':", json_data["errors"])
        return None

    column_id = json_data["data"]["create_column"]["id"]
    print(f"✅ Created column: {title} (ID: {column_id})")
    return column_id


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
        print(f"Error creating group '{group_name}':", json_data["errors"])
        return None
    return json_data["data"]["create_group"]["id"]

def create_item(board_id, group_id, task_name, time_estimation, column_ids):
    column_values = {column_ids["Time Estimation"]: float(time_estimation)}
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
        print(f"Error creating item '{task_name}':", json_data["errors"])
    else:
        print(f"Created item: {task_name} ⏱ {time_estimation}")

def get_board_groups(board_id):
    query = f'''
    query {{
      boards(ids: {board_id}) {{
        groups {{
          id
          title
        }}
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    json_data = response.json()
    return json_data["data"]["boards"][0]["groups"]

def delete_group(board_id, group_id):
    query = f'''
    mutation {{
      delete_group (board_id: {board_id}, group_id: "{group_id}") {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=HEADERS)
    if response.ok:
        print(f"Deleted default group with ID: {group_id}")

def create_full_board(board_name, board_data, extra_columns=None):
    if extra_columns is None:
        extra_columns = []

    print(f"Creating board: {board_name}")
    board_id = create_board(board_name)
    if not board_id:
        print("Failed to create board.")
        return

    print(f" Board URL: https://app.monday.com/boards/{board_id}")

    # Create required and extra columns
    column_ids = {}
    column_ids["Time Estimation"] = create_column(board_id, "Time Estimation", "numbers")
    if not column_ids["Time Estimation"]:
        print("Failed to create Time Estimation column.")
        return

    for col in extra_columns:
      defaults = None
      if col["type"] == "status" and "labels" in col:
          defaults = json.dumps({"labels": col["labels"]}).replace('"', '\\"')  # double-escape quotes
      col_id = create_column(
          board_id,
          col["title"],
          col["type"],
          defaults=defaults,
          description=col.get("description")
      )
      if col_id:
          column_ids[col["title"]] = col_id


    # Add first group and items
    first_group = board_data[0]
    if not first_group.get("items"):
        print("First group has no items. Aborting to avoid orphan state.")
        return

    first_group_id = create_group(board_id, first_group["group"])
    if not first_group_id:
        print("Failed to create first group.")
        return

    for item in first_group["items"]:
        create_item(
            board_id,
            first_group_id,
            item["task"],
            item["time_estimation"],
            column_ids
        )

    # Delete default group after first group is added
    existing_groups = get_board_groups(board_id)
    for group in existing_groups:
        if group["id"] != first_group_id:
            print(f"Removing initial group: {group['title']} (ID: {group['id']})")
            delete_group(board_id, group["id"])

    # Add remaining groups
    for group in board_data[1:]:  # Skip first group (already added)
        if not group.get("items"):
            continue
        group_id = create_group(board_id, group["group"])
        if not group_id:
            continue
        for item in group["items"]:
            create_item(
                board_id,
                group_id,
                item["task"],
                item["time_estimation"],
                column_ids
            )

    print(f" Board '{board_name}' created successfully.")