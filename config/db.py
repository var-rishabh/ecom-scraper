from config.logger import logger

from pymongo import MongoClient


# connect to the mongo database
def connect_to_mongo():
    try:
        # local mongo
        # client = MongoClient("mongodb://localhost:27017/")

        # container mongo
        # client = MongoClient(f"mongodb://r3f:r3f@mongodb:27017/")

        # aws mongo
        client = MongoClient("mongodb://r3f:r3f@13.127.228.27:27017/")
        db = client["ecomScrapper"]
        return db

    except Exception as e:
        logger.error(f"Error connecting to mongo.", exc_info=True)
        return None
