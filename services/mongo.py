from pymongo import MongoClient as PyMongoClient
from constants import environment

class MongoClient:
    _instance = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            connection_string = f"mongodb+srv://{environment['mongo_user']}:{environment['mongo_password']}@jobsweebcluster0.x1z6x.mongodb.net/Jobsweep-Database?retryWrites=true&w=majority&appName=JobsweebCluster0"
            client = PyMongoClient(connection_string)
            cls._db = client['Jobsweep-Database']
        return cls._db
