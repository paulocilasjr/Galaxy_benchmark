import time
from dotenv import load_dotenv
load_dotenv()
import os
from bioblend.galaxy import GalaxyInstance
gi = GalaxyInstance(url='https://usegalaxy.org/', key=os.getenv('GALAXY_API_KEY'))
job_id = 'bbd44e69cb8906b5098451079916e0a5'
while True:
    state = gi.jobs.get_state(job_id)
    print(state)
    if state in ['ok', 'error', 'failed', 'deleted']:
        break
    time.sleep(60)