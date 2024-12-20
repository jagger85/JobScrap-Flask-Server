from pymongo import MongoClient as PyMongoClient
from constants import environment

class MongoClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            connection_string = f"mongodb+srv://{environment.MONGO_USER}:{environment.MONGO_PASSWORD}@jobsweebcluster0.x1z6x.mongodb.net/?retryWrites=true&w=majority&appName=JobsweebCluster0"
            cls._instance = PyMongoClient(connection_string)
        return cls._instance

# Usage
mongo_client = MongoClient()