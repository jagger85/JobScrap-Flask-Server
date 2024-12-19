from brightdata.brightdata_api import BrightDataClient as api
from models import IndeedParams, LinkedInParams
from data_handler.storage_factory import StorageFactory
from data_handler.storage_type import StorageType
import logging
from logger.logger import get_logger, set_log_level

if __name__ == "__main__":
    global log
    log = get_logger("App")
    set_log_level(logging.INFO)

    client = api(get_logger("BrightApi"))
    data_handler = StorageFactory.get_storage_handler(StorageType.JSON)

    indeed_params = IndeedParams()
    linkedIn_params = LinkedInParams()

    log.info(indeed_params.get_dataset_id())
    log.info(linkedIn_params.get_dataset_id())

    response = client.retrieve_snapshots_list(indeed_params.get_dataset_id)
    if response.get("status") == "error":
        log.error(response.get("message"))
    elif response.get("status") == "success":
        log.info(response.get("message"))
        data_handler.store_snapshot_list(
            indeed_params.get_platform_name(), response.get("data")
        )
