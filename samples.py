import random
import string

def createUniqueName():
    prefix = "d_"
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=17))
    return f"{prefix}{random_string}"

def return_dataset_id():
    return {"dataset_id": createUniqueName()}

def return_dataset():
    return {"name": "Sample Dataset", "data": [1, 2, 3, 4, 5] }
