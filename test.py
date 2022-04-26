import time
import logging
import sys

console_handler = logging.StreamHandler(stream=sys.stdout)
console_handler.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[console_handler])


  # can be logging.DEBUG or logging.INFO as well

logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_haj():

    for i in range(10):
        logger.info('-----------------')
        time.sleep(2)

