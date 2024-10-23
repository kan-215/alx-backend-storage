#!/usr/bin/env python3
from pymongo import MongoClient

# Connect to the MongoDB server and access the logs database
client = MongoClient()
db = client.logs
collection = db.nginx

# Get the total number of documents in the collection
log_count = collection.count_documents({})

# Display the total log count
print(f"{log_count} logs")

# Display method counts
methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
print("Methods:")
for method in methods:
    method_count = collection.count_documents({"method": method})
    print(f"\tmethod {method}: {method_count}")

# Count documents with method GET and path /status
status_check_count = collection.count_documents({"method": "GET", "path": "/status"})
print(f"{status_check_count} status check")
