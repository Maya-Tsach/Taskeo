import os
import json
import requests

API_URL = "https://api.monday.com/v2"

def make_headers(api_key):
    return {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

def rename_board(board_id, new_name, api_key):
    query = f'''
    mutation {{
      update_board(board_id: {board_id}, board_attribute: name, new_value: "{new_name}")
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    
    if "errors" in json_data:
        print("❌ Error renaming board:", json_data["errors"])
    else:
        print(f"✅ Board renamed to: {new_name}")

def create_board(board_name, api_key):
    query = f'''
    mutation {{
      create_board (board_name: "{board_name}", board_kind: private) {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    if "errors" in json_data:
        print("❌ Error creating board:", json_data["errors"])
        return None
    board_id = json_data["data"]["create_board"]["id"]
    print(f"✅ Board created: {board_name} (ID: {board_id})")
    return board_id


def get_columns(board_id, api_key):
    query = f'''
    query {{
      boards(ids: {board_id}) {{
        columns {{
          id
          title
        }}
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    return json_data["data"]["boards"][0]["columns"]

def delete_column(board_id, column_id, api_key):
    query = f'''
    mutation {{
      delete_column (board_id: {board_id}, column_id: "{column_id}") {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    if response.ok:
        print(f"🗑️ Deleted column: {column_id}")
    else:
        print(f"❌ Failed to delete column {column_id}: {response.text}")

def create_column(board_id, title, column_type="numbers", defaults=None, description=None, api_key=None):
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
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()

    print("📥 API Response:")
    print(json.dumps(json_data, indent=2))

    if "errors" in json_data:
        print(f"❌ Error creating column '{title}':", json_data["errors"])
        return None

    column_id = json_data["data"]["create_column"]["id"]
    print(f"✅ Created column: {title} (ID: {column_id})")
    return column_id

def create_group(board_id, group_name, api_key):
    query = f'''
    mutation {{
      create_group (board_id: {board_id}, group_name: "{group_name}") {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    if "errors" in json_data:
        print(f"Error creating group '{group_name}':", json_data["errors"])
        return None
    return json_data["data"]["create_group"]["id"]

def create_item(board_id, group_id, task_name, time_estimation_AI, column_ids, api_key):
    column_values = {column_ids["Time Estimation AI"]: float(time_estimation_AI)}
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
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    if "errors" in json_data:
        print(f"Error creating item '{task_name}':", json_data["errors"])
    else:
        print(f"📝 Created item: {task_name} ⏱ {time_estimation_AI}")

def get_board_groups(board_id, api_key):
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
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    json_data = response.json()
    return json_data["data"]["boards"][0]["groups"]

def delete_group(board_id, group_id, api_key):
    query = f'''
    mutation {{
      delete_group (board_id: {board_id}, group_id: "{group_id}") {{
        id
      }}
    }}
    '''
    response = requests.post(API_URL, json={'query': query}, headers=make_headers(api_key))
    if response.ok:
        print(f"🗑️ Deleted default group with ID: {group_id}")

def create_full_board(board_name, board_data, extra_columns=None, api_key=None, board_id=None):
    if extra_columns is None:
        extra_columns = []

    if board_id:
        print(f"🔁 Using existing board ID: {board_id}")
        rename_board(board_id, board_name, api_key)
    else:
        print(f"🆕 Creating board: {board_name}")
        board_id = create_board(board_name, api_key)
        if not board_id:
            print("❌ Failed to create board.")
            return

    print(f"🔗 Board URL: https://app.monday.com/boards/{board_id}")

    # 🧹 Delete all existing columns first
    columns = get_columns(board_id, api_key)
    for col in columns:
        delete_column(board_id, col["id"], api_key)

    # ➕ Create new columns
    column_ids = {}
    column_ids["Time Estimation AI"] = create_column(board_id, "Time Estimation AI", "numbers", api_key=api_key)
    if not column_ids["Time Estimation AI"]:
        print("❌ Failed to create Time Estimation AI column.")
        return

    for col in extra_columns:
        defaults = None
        if col["type"] == "status" and "labels" in col:
            defaults = json.dumps({"labels": col["labels"]}).replace('"', '\\"')
        col_id = create_column(
            board_id,
            col["title"],
            col["type"],
            defaults=defaults,
            description=col.get("description"),
            api_key=api_key
        )
        if col_id:
            column_ids[col["title"]] = col_id

    first_group = board_data[0]
    if not first_group.get("items"):
        print("❌ First group has no items. Aborting to avoid orphan state.")
        return

    first_group_id = create_group(board_id, first_group["group"], api_key)
    if not first_group_id:
        print("❌ Failed to create first group.")
        return

    for item in first_group["items"]:
        create_item(
            board_id,
            first_group_id,
            item["task"],
            item["time_estimation_AI"],
            column_ids,
            api_key
        )

    existing_groups = get_board_groups(board_id, api_key)
    for group in existing_groups:
        if group["id"] != first_group_id:
            print(f"🗑️ Removing initial group: {group['title']} (ID: {group['id']})")
            delete_group(board_id, group["id"], api_key)

    for group in board_data[1:]:
        if not group.get("items"):
            continue
        group_id = create_group(board_id, group["group"], api_key)
        if not group_id:
            continue
        for item in group["items"]:
            create_item(
                board_id,
                group_id,
                item["task"],
                item["time_estimation_AI"],
                column_ids,
                api_key
            )

    print(f"✅ Board '{board_name}' populated successfully.")
