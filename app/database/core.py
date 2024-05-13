from pymongo import MongoClient
import datetime
import datetime

# Connect to the MongoDB server
client = MongoClient('mongodb+srv://lol:LeXuqMIbJBgsujrQ@root.nh1cxhu.mongodb.net/')

# Select your database
db = client['Lol']

# Select the collection where you want to store the results
collection = db['live']

def save_draft_analysis(team, enemy, config, result):
    # Structure the document to be saved
    document = {
        'team': team,
        'enemy': enemy,
        'config': config,
        'result': result,
        'timestamp': datetime.datetime.utcnow()  # Optional: add a timestamp
    }

    # Insert the document into the collection
    result = collection.insert_one(document)

def load_all_data():
    """
    Loads all documents from the specified MongoDB collection.
    
    Returns:
        A list of dictionaries, where each dictionary represents a document.
    """
    try:
        documents = collection.find()  # No filter criteria, loads all documents

        print('load_all_data', documents)
        return list(documents)  # Convert the cursor to a list
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
        return []  # Return an empty list in case of error
