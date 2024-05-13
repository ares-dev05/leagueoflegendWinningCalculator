from flask import request, Blueprint, jsonify
import http.client
import json
from ..packages.core import Role, analyze_draft
from .utils import save_to_file, load_from_file
from ..database.core import save_draft_analysis, load_all_data

DATASET_VERSION = "4"

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return 'Goodbye, World!'

@main.route('/save/<name>')
def save_data(name):
    dataset = fetch_dataset(name);

    if dataset:
        save_to_file(dataset, f'{name}.json')
    return "Data saved to file"

@main.route('/load/<name>')
def load_data(name):
    data = load_from_file(f'{name}.json')

    if data is not None:
        return jsonify(data)
    else:
        return "Data not found", 404

def fetch_dataset(name):
    conn = http.client.HTTPSConnection("bucket.draftgap.com")
    try:
        conn.request("GET", f"/datasets/v4/{name}.json")
        res = conn.getresponse()
        if res.status == 200:
            data = res.read()
            return json.loads(data)
        else:
            print(f"Error fetching dataset: HTTP {res.status}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

@main.route('/history')
def load_match_history():
    data = load_all_data()

    if data is not None:
        for document in data:
            document['_id'] = str(document['_id'])
        return jsonify(data) 
    else:
        return "Data not found", 404

@main.route('/analyze_draft', methods=['GET', 'POST'])
def analyze_draft_route():
    # Assuming you're receiving the data as JSON
    if request.method == 'POST':
        data = request.json
    else:  # For GET, you might pass parameters in the query string
        data = request.args.to_dict()

    # Now, process the data to fit the analyze_draft function's expected format
    team, enemy, config = process_data(data)

    dataset = load_from_file('current-patch.json')
    fullDataset = load_from_file('30-days.json')

    # Call the analyze_draft function with processed data
    result = analyze_draft(dataset, fullDataset, team, enemy, config)

    save_draft_analysis(data['team'], data['enemy'], config, result);

    # Return the result as JSON
    return jsonify(result)

def process_data(data):
    # Convert team and enemy lists to dictionaries with Role enum keys
    team = {Role(role): champion_key for role, champion_key in data['team']}
    enemy = {Role(role): champion_key for role, champion_key in data['enemy']}

    # Directly use the config dictionary from the data
    config = data['config']

    return team, enemy, config