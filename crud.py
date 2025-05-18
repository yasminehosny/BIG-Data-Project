from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017) 
db = client.get_database('BDProject') 


def insert_document(table_name, data, many=False):
    collection = db[table_name]
    try:
        if many:
            result = collection.insert_many(data)
            print(f"Inserted documents with ids: {result.inserted_ids}")
            return result.inserted_ids
        else:
            result = collection.insert_one(data)
            print(f"Inserted document with id: {result.inserted_id}")
            return result.inserted_id
    except Exception as e:
        print(f"Error inserting document(s): {e}")


def read_document(table_name, filter_condition=None, many=True):
    collection = db[table_name]
    try:
        if filter_condition is None:
            filter_condition = {}

        if many:
            documents = list(collection.find(filter_condition))
            print(f"Found {len(documents)} document(s)")
            for doc in documents:
                print(doc)
            return documents
        else:
            document = collection.find_one(filter_condition)
            print("Found one document:", document)
            return document
    except Exception as e:
        print(f"Error reading document(s): {e}")


def update_document(table_name, filter_condition, update_data, many=True):
    collection = db[table_name]
    try:
        if many:
            result = collection.update_many(filter_condition, {"$set": update_data})
        else:
            result = collection.update_one(filter_condition, {"$set": update_data})
        print(f"Matched {result.matched_count}, Modified {result.modified_count} document(s)")
    except Exception as e:
        print(f"Error updating document(s): {e}")


def delete_document(table_name, filter_condition, many=True):
    collection = db[table_name]
    try:
        if many:
            result = collection.delete_many(filter_condition)
        else:
            result = collection.delete_one(filter_condition)
        print(f"Deleted {result.deleted_count} document(s)")
    except Exception as e:
        print(f"Error deleting document(s): {e}")


projects = [
    {
        "name": "Solar Plant A",
        "country": "Egypt",
        "status": "Operational",
        "latitude": 26.8,
        "longitude": 31.1,
        "product": "Electricity"
    },
    {
        "name": "Wind Farm B",
        "country": "Morocco",
        "status": "Planned",
        "latitude": 34.2,
        "longitude": -5.9,
        "product": "Electricity"
    },
    {
        "name": "Hydrogen Project C",
        "country": "UAE",
        "status": "Under Construction",
        "latitude": 24.5,
        "longitude": 54.3,
        "product": "Green Hydrogen"
    }
]

project = {
    "name": "New Wind Farm",
    "country": "Jordan",
    "status": "Operational",
    "latitude": 32.3,
    "longitude": 36.2,
    "product": "Electricity"
}



print("\n=== INSERT MANY ===")
insert_document("projects", projects, many=True)

print("\n=== INSERT ONE ===")
insert_document("projects", project, many=False)

print("\n=== READ ALL ===")
read_document("projects", many=True)

print("\n=== READ ONE (by name) ===")
read_document("projects", {"name": "Solar Plant A"}, many=False)

print("\n=== UPDATE ONE (Wind Farm B -> Operational) ===")
update_document("projects", {"name": "Wind Farm B"}, {"status": "Operational"}, many=False)

print("\n=== UPDATE MANY (Operational -> Upgraded) ===")
update_document("projects", {"status": "Operational"}, {"status": "Upgraded"}, many=True)

print("\n=== DELETE ONE (Hydrogen Project C) ===")
delete_document("projects", {"name": "Hydrogen Project C"}, many=False)

print("\n=== DELETE MANY (status = Planned) ===")
delete_document("projects", {"status": "Planned"}, many=True)


