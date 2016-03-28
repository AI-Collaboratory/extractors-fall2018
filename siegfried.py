#!/usr/bin/env python
"""Siegfried extracts the file format with respect to the PRONOM registry."""
import subprocess
import logging
import json
import datetime
from config import *
import pyclowder.extractors as extractors
from requests.exceptions import HTTPError


def main():
    global extractorName, messageType, rabbitmqExchange, rabbitmqURL

    # set logging
    logging.basicConfig(format='%(levelname)-7s : %(name)s -  %(message)s',
                        level=logging.WARN)
    logging.getLogger('pyclowder.extractors').setLevel(logging.INFO)

    # connect to rabbitmq
    extractors.connect_message_bus(extractorName=extractorName,
                                   messageType=messageType,
                                   processFileFunction=process_file,
                                   rabbitmqExchange=rabbitmqExchange,
                                   rabbitmqURL=rabbitmqURL)


# ----------------------------------------------------------------------
# Process the file and upload the results
def process_file(parameters):
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)
    global extractorName

    inputfile = parameters['inputfile']
    _logger.info("Got a process_file request: "+inputfile)

    # call the Siegfried (sf) program
    resultStr = subprocess.check_output(['sf', '-json', inputfile],
                                        stderr=subprocess.STDOUT)

    _logger.info(resultStr)
    result = json.loads(resultStr)

    afile = result['files'][0]  # always one file only

    content = {}  # assertions about the file
    content['dcterms:extent'] = afile['filesize']

    matches = []
    for match in afile['matches']:
        _logger.info(match)
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
        "created_at": datetime.datetime.now(pytz.utc).isoformat()
    }

    _logger.info("JSON-LD: {0}".format(json.dumps(jsonld_wrap)))

    # upload metadata (metadata is a JSON-LD array of dict)
    try:
        extractors.upload_file_metadata_jsonld(mdata=jsonld_wrap,
                                               parameters=parameters)
    except HTTPError as e:
        _logger.error(e)
        _logger.error("HTTP Error: ".format(e.response.text))
        pass


if __name__ == "__main__":
    main()
