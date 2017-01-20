#!/usr/bin/env python
"""Siegfried extracts the file format with respect to the PRONOM registry."""
import subprocess
import logging
import json
import datetime
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

        content = {}  # assertions about the file
        content['dcterms:extent'] = afile['filesize']

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
            content['dcterms:conformsTo'] = matches
        # elif len(matches) == 1:
        #    content['dcterms:conformsTo'] = matches[0]
        # content = matches[0]

        jsonld_wrap = {
            "@context": {
                "med": "http://medici.ncsa.illinois.edu/",
                "extractor_id": {
                  "@id": "med:extractor/id",
                  "@type": "@id"
                },
                "user_id": {
                  "@id": "med:user/id",
                  "@type": "@id"
                },
                "created_at": {
                  "@id": "http://purl.org/dc/terms/created",
                  "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
                },
                "agent": {
                  "@id": "http://www.w3.org/ns/prov#Agent"
                },
                "user": "med:user",
                "extractor": "med:extractor",
                "content": {
                  "@id": "http://medici.ncsa.illinois.edu/metadata/content"
                },
                "file_id": {
                  "@id": "http://medici.ncsa.illinois.edu/metadata/file_id"
                },
                "sf": "http://www.itforarchivists.com/siegfried/",
                "dcterms": "http://purl.org/dc/terms/"
            },
            "content": content,
            "agent": {
                "@type": "cat:extractor",
                "name": "Siegfried Extractor (PRONOM format identification)",
                "extractor_id":
                    "https://dts.ncsa.illinois.edu/api/extractors/siegfried"
            },
            "created_at": datetime.datetime.utcnow().isoformat()
        }

        logger.info("JSON-LD: {0}".format(json.dumps(jsonld_wrap)))

        # upload metadata (metadata is a JSON-LD array of dict)
        pyclowder.files.upload_metadata(connector, host, secret_key, file_id, jsonld_wrap)


if __name__ == "__main__":
    extractor = Siegfried()
    extractor.start()
