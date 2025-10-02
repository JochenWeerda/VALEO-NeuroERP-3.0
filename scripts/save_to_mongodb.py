import sys
import os
from pymongo import MongoClient
from datetime import datetime

def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['valeo_neuroerp']
    return db

def save_document(db, filepath):
    collection = db['documents']
    
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        
    document = {
        'filename': os.path.basename(filepath),
        'path': filepath,
        'content': content,
        'created_at': datetime.utcnow(),
        'type': 'planning_document',
        'metadata': {
            'phase': 'planning',
            'status': 'completed',
            'next_phase': 'create',
            'version': '1.0',
            'author': 'Claude',
            'tags': ['planning', 'documentation', 'handover']
        }
    }
    
    result = collection.insert_one(document)
    print(f"Saved {filepath} with ID: {result.inserted_id}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python save_to_mongodb.py file1 [file2 ...]")
        sys.exit(1)
        
    db = connect_to_mongodb()
    
    for filepath in sys.argv[1:]:
        if os.path.exists(filepath):
            save_document(db, filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == '__main__':
    main() 