from brightdata.brightdata_api import BrightDataClient as api
from models.IndeedParams import IndeedParams
from models.LinkedInParams import LinkedInParams
from file_handler.file_factory import FileFactory
import logging
from logger import get_logger, set_log_level

if __name__ == "__main__":
    
    global log
    log = get_logger("App")
    set_log_level(logging.DEBUG)

    client = api(get_logger("BrightApi"))
    file_factory = FileFactory()

    indeed_params = IndeedParams()
    linkedIn_params= LinkedInParams()

    log.info(indeed_params.get_dataset_id())
    log.info(linkedIn_params.get_dataset_id())

    response = client.retrieve_snapshots_list(indeed_params.get_dataset_id)
    log.info(response.data)
   # file_factory.save_snapshot_list(request, indeed_params.get_platform_name)

