import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# connect to the mongo database
def connect_to_mongo():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB_NAME")]
    collection = db[os.getenv("MONGO_COLLECTION_NAME")]

    return collection
