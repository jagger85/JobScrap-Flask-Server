class BrightDataClientSimulation:
    def __init__(self):
        self.dataset_id = None

    def request_dataset(self, params):
        # Simulate setting a dataset ID
        self.dataset_id = "simulated_dataset_id"
        return {
            "status": "error",
            "message": "Simulated dataset request shit",
        }

    def check_dataset_status(self):
        # Simulate a ready status
        return {
            "status": "ready",
            "message": "Simulated dataset is ready for retrieval",
        }

    def retrieve_dataset(self):
        # Simulate dataset retrieval
        return {
            "status": "success",
            "message": "Simulated dataset retrieved successfully",
            "data": {"example_key": "example_value"},
        }


if __name__ == "__main__":
    client = BrightDataClientSimulation()
    # Example usage
    params = {
        "keyword": "software engineer",
        "location": "New York",
    }  # Simulated params
    print(client.request_dataset(params))
    print(client.check_dataset_status())
    print(client.retrieve_dataset())
