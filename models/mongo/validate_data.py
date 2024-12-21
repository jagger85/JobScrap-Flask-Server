def validate_data(data, required_fields):
    for field in required_fields:
        if field not in data:
            print(f"value missing {field}")
            return False
    return True