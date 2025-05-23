class BaseModel:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def create(self, data):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def validate_data(self, data, required_fields):
        for field in required_fields:
            if field not in data:
                print(f"value missing {field}")
                return False
        return True