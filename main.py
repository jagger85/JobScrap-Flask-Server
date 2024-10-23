from samples import return_dataset_id, return_dataset
from file_handler.file_manager import FileManager


def test_file_handler():
    # Initialize the FileManager
    file_manager = FileManager()

    # Get the dataset ID from the API
    dataset_info = return_dataset_id()
    dataset_id = dataset_info["dataset_id"]  # Correct key usage

    # Simulate a sample dataset
    sample_dataset = return_dataset()

    # Process the dataset and dataset ID
    file_manager.process_dataset_id(dataset_id)
    file_manager.process_dataset(sample_dataset, dataset_id)


if __name__ == "__main__":
    test_file_handler()
