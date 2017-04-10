#!/usr/bin/env python
"""Siegfried extracts the file format with respect to the PRONOM registry."""
import subprocess
import logging
import json
from pyclowder.extractors import Extractor
import pyclowder.files


class Siegfried(Extractor):
    """Use byte patterns from the PRONOM registry to attempt to determine file format."""
    def __init__(self):
        Extractor.__init__(self)

        # add any additional arguments to parser
        # self.parser.add_argument('--max', '-m', type=int, nargs='?', default=-1,
        #                          help='maximum number (default=-1)')

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the exctractor
        logging.getLogger('pyclowder').setLevel(logging.DEBUG)
        logging.getLogger('__main__').setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        logger = logging.getLogger(__name__)

        inputfile = resource["local_paths"][0]
        file_id = resource['id']
        logger.info("Got a process_file request: "+inputfile)

        # call the Siegfried (sf) program
        resultStr = subprocess.check_output(['sf', '-json', inputfile],
                                            stderr=subprocess.STDOUT)

        logger.info(resultStr)
        result = json.loads(resultStr)

        afile = result['files'][0]  # always one file only

        result = {}  # assertions about the file
        result['extent'] = afile['filesize']

        matches = []
        for match in afile['matches']:
            logger.info(match)
            m = {}
            if 'id' in match:
                m['@id'] = 'info:pronom/'+match['id']
            if 'format' in match:
                m['sf:name'] = match['format']
            if 'version' in match:
                if len(match['version'].strip()) > 0:
                    m['sf:version'] = match['version']
            if 'mime' in match:
                m['sf:mime'] = match['mime']
            if 'basis' in match:
                m['sf:basis'] = match['basis']
            matches.append(m)

        if len(matches) > 0:
            result['conformsTo'] = matches

        metadata = self.get_metadata(result, 'file', file_id, host)

        # upload metadata (metadata is a JSON-LD array of dict)
        pyclowder.files.upload_metadata(connector, host, secret_key, file_id, metadata)


if __name__ == "__main__":
    extractor = Siegfried()
    extractor.start()
