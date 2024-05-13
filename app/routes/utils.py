import json
import os

# Assuming YourFlaskApp is your current working directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

def save_to_file(data, filename="dataset.json"):
    # Ensure the data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, 'w') as f:
        json.dump(data, f)

def load_from_file(filename="dataset.json"):
    file_path = os.path.join(DATA_DIR, filename)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
