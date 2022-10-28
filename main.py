import subprocess
from pathlib import Path
import os
from os.path import join, isfile
import logging

# setup paths to data
data = Path(os.getenv('DATA_PATH', '/data'))

data.mkdir(exist_ok=True)

inputs = data / 'inputs'

outputs = data / 'outputs'

outputs.mkdir(exist_ok=True)

logger = logging.getLogger('tools-unzip')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(outputs / 'tools-unzip.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# get list of files to extract
files = [f for f in os.listdir(data) if isfile(join(data, f))]
logger.info('Archives found: %s' %files)

# run the extact process
logger.info('Running extract process')
for archive in files:
    if archive.split('.')[-1:][0] == 'zip':
        logger.info('Running an unzip')
        subprocess.call(['unzip',
                         join('/data/inputs', archive),    # source
                         '-d', outputs,         # destination directory
                         ])

logger.info('Extract completed')


# create json for metadata for outputs
