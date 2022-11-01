import subprocess
from pathlib import Path
import os
from os.path import join, isfile
import logging



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

outputs = data / 'outputs'

outputs.mkdir(exist_ok=True)

metaadata_output = outputs / 'metadata'

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
    print(archive)
    if archive.split('.')[-1:][0] == 'zip':
        logger.info('Running an unzip')
        subprocess.call(['unzip',
                         join('/data/inputs', archive),    # source
                         '-d', outputs,         # destination directory
                         ])
    break

logger.info('Extract process completed')

logger.info('Starting process of generating metadata json file')
# create json for metadata for outputs
# this should read the name of the input file and run
# udm data will be in the format UDM_SSPX_YYYY_FZstatus
# there may also be a metadata file which can be used
archive_name = archive.split('.')[0]
print(archive_name)

# parse to get the details of the run
model, ssp, year, floodzone = archive_name.split('_')

logger.info('Got and parsed name of archive')

# set the output title, description and so on
output_title = ''
output_description = ''

output_path = metadata_output
file_name = 'metadata'

# generate the json metadata file passing the key fields we want to populate
metadata_json(output_path, output_title, output_description, bbox, file_name, keyword)
logger.info('Completed process of generating metadata file')

# completed script

