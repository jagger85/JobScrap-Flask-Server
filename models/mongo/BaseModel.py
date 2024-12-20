class BaseModel:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def find_all(self):
        return list(self.collection.find())
    
    def create(self, data):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)