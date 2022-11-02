import subprocess
from pathlib import Path
import os
from os.path import join, isfile
import logging
import pandas as pd
from shutil import copyfile
import rasterio
import json
import geopandas as gpd
from shapely.geometry import box
from datetime import datetime


def metadata_json(output_path, output_title, output_description, bbox, file_name, keyword):
    """
    Generate a metadata json file used to catalogue the outputs of the UDM model on DAFNI
    """

    # Create metadata file
    metadata = f"""{{
      "@context": ["metadata-v1"],
      "@type": "dcat:Dataset",
      "dct:language": "en",
      "dct:title": "{output_title}",
      "dct:description": "{output_description}",
      "dcat:keyword": ["{keyword}"
      ],
      "dct:subject": "Environment",
      "dct:license": {{
        "@type": "LicenseDocument",
        "@id": "https://creativecommons.org/licences/by/4.0/",
        "rdfs:label": null
      }},
      "dct:creator": [{{"@type": "foaf:Organization"}}],
      "dcat:contactPoint": {{
        "@type": "vcard:Organization",
        "vcard:fn": "DAFNI",
        "vcard:hasEmail": "support@dafni.ac.uk"
      }},
      "dct:created": "{datetime.now().isoformat()}Z",
      "dct:PeriodOfTime": {{
        "type": "dct:PeriodOfTime",
        "time:hasBeginning": null,
        "time:hasEnd": null
      }},
      "dafni_version_note": "created",
      "dct:spatial": {{
        "@type": "dct:Location",
        "rdfs:label": null
      }},
      "geojson": {bbox}
    }}
    """

    # write to file
    with open(join(output_path, '%s.json' % file_name), 'w') as f:
        f.write(metadata)
    return


# setup paths to data
data = Path(os.getenv('DATA_PATH', '/data'))

data.mkdir(exist_ok=True)

inputs = data / 'inputs'

data_input = inputs / 'data'

outputs = data / 'outputs'

outputs.mkdir(exist_ok=True)

metadata_output = outputs / 'metadata'
metadata_output.mkdir(exist_ok=True)

logger = logging.getLogger('intake')
logger.setLevel(logging.INFO)
fh = logging.FileHandler(outputs / 'intake.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


# parse input vars from user
file_to_copy = os.getenv('file_to_copy')
if file_to_copy is None:
    logger.info('Failed as file to copy var not passed')
    print('Failed as file to copy not passed')
    exit()

keyword = os.getenv('keyword')
if keyword is None:
    keyword = 'OpenCLIM'


# get list of files to extract
files = [f for f in os.listdir(data_input) if isfile(join(data_input, f))]
logger.info('Archives found: %s' %files)
print(files)

# run the extact process
logger.info('Running extract process')
for archive in files:
    print(archive)
    archive = archive
    if archive.split('.')[-1:][0] == 'zip':
        logger.info('Running an unzip')
        subprocess.call(['unzip',
                         join(data_input, archive),    # source
                         '-d', inputs,         # destination directory
                         ])
    break

logger.info('Extract process completed')

# this should read the name of the input file and run
# udm data will be in the format UDM_SSPX_YYYY_FZstatus
# there may also be a metadata file which can be used
archive_name = archive.split('.')[0]
print(archive_name)

# parse to get the details of the run
model, ssp, year, floodzone = archive_name.split('-')
logger.info('Got and parsed name of archive')


# select out_cell_dph.asc  - let use select the file, so out_cell_dph is default
# file_to_copy = 'out_cell_dph.asc' # defined by user input
file_to_copy_output_name = 'out_cell_dph-%s_%s_%s.asc' %(ssp,year,floodzone)
copyfile('data/inputs/%s/%s' %(archive_name, file_to_copy),'data/outputs/%s' %(file_to_copy_output_name))


# contraints and attractors to be included
logger.info('Starting process of generating key parameters file')

# read in constaints file 
constraints = pd.read_csv('data/inputs/%s/constraints.csv' %archive_name)

# read in attractors file
attractors = pd.read_csv('data/inputs/%s/attractors.csv' %archive_name)


# write new file
with open('data/outputs/key_parameters.csv', 'w') as f:
    f.write('PARAMETER, VALUE\n')
    f.write('SSP, %s\n' %ssp)
    f.write('YEAR, %s\n' %year)
    if floodzone == 'withfz':
        f.write('FLOODZONE, TRUE\n')
    else:
        f.write('FLOODZONE, FALSE\n')

    # attractors
    f.write('ATTRACTORS, %s\n' %attractors.to_string(header=False,index=False,index_names=False))

    # contraints
    f.write('CONSTRAINTS, %s\n' %constraints.to_string(header=False,index=False,index_names=False))


logger.info('Completed process of generating key parameters file')

logger.info('Starting process of generating metadata json file')

# create json for metadata for outputs
# set the output title, description and so on
output_title = 'UFG Outputs - %s_%s_%s' %(ssp,year,floodzone)
output_description = 'Outputs from the UFG model for a run of the UDM model. Scenario parameters: SSP=%s, YEAR=%s, Floodzone:%s. Output includes a key parameters file containing the parameter values linked to each run' %(ssp, year, floodzone)

output_path = metadata_output
file_name = 'metadata'

image = rasterio.open('data/outputs/%s' %(file_to_copy_output_name))

bbox = json.dumps({'type':'Feature','properties':{},'geometry':gpd.GeoSeries(box(*image.bounds), crs='EPSG:27700').to_crs(epsg=4326).iloc[0].__geo_interface__})

# generate the json metadata file passing the key fields we want to populate
metadata_json(output_path, output_title, output_description, bbox, file_name, keyword)
logger.info('Completed process of generating metadata file')

# completed script

