from pymongo import MongoClient as PyMongoClient
from constants import environment
from models import UserModel, OperationModel

# Create a single instance at module level
_connection_string = f"mongodb+srv://{environment['mongo_user']}:{environment['mongo_password']}@jobsweebcluster0.x1z6x.mongodb.net/Jobsweep-Database?retryWrites=true&w=majority&appName=JobsweebCluster0"
_client = PyMongoClient(_connection_string)
_db = _client['Jobsweep-Database']

# Export the models as module-level variables
user_model = UserModel(_db)
operation_model = OperationModel(_db)
