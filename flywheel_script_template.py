# This is a template for a python script that can be processed by
# the flywheel_script_gear.

import flywheel
import logging

# defina a logger
logger = logging.getLogger(__name__)

# this is the script that is run by the gear
def flywheel_script(message):
    logger.info('this is a description of what the script will do.')

    # the message comes from the gear
    fw = message['fw']
    image = fw.get_file(message['file_id'])



if __name__ == "__main__":
    # local testing, requires a valid flywheel file
    # attach to flyhweel, fill in with your api key
    fw = flywheel.Client('flywheelaz.uwhealth.org:djEl4p5F0JNRNnkuqAeuT-uzho21Cu9ny96A43jwrPg4-CdejUgXlJFPA', request_timeout=1000)

    test_file = fw.resolve('prostatespore/fws_test_project/fws_test_subject/fws_test_session/PET/PET AC Prostate.zip')

    message = {
        'file': test_file,
        'script_name': 'test_script.py'
    }

    flywheel_script(message)




