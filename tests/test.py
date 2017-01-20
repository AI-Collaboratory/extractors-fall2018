import requests
import json
import os
import time


def main():
    """Test BD extractor"""
    print("Running extract test")
    print(json.dumps(extract('localhost', 'iSchool.jpg'), indent=2))


def extract(dts, file, wait=60, key=''):
    """
    Extract derived data from the given input file's contents via DTS.
    @param dts: The URL to the Data Tilling Service to use.
    @param file: The input file.
    @param wait: The amount of time to wait for the DTS to respond.  Default is 60 seconds.
    @param key: The key for the DTS. Default is ''.
    @return: The filename of the JSON file containing the extracted data.
    """
    username = 'user@example.com'
    password = '1example'
    metadata = ''

    # Check for authentication
    if '@' in dts:
        parts = dts.rsplit('@', 1)
        dts = parts[1]
        parts = parts[0].split(':')
        username = parts[0]
        password = parts[1]

    # Upload file
    file_id = ''

    if(file.startswith('http://')):
        data = {}
        data["fileurl"] = file

        if key:
            file_id = requests.post(
                'http://' + dts + ':9000/api/extractions/upload_url?key=' + key,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)).json()['id']
        else:
            file_id = requests.post(
                'http://' + dts + ':9000/api/extractions/upload_url',
                auth=(username, password),
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data)).json()['id']
    else:
        if key:
            file_id = requests.post(
                'http://' + dts + ':9000/api/extractions/upload_file?key=' + key,
                files={'File': (os.path.basename(file), open(file))}).json()['id']
        else:
            file_id = requests.post(
                'http://' + dts + ':9000/api/extractions/upload_file',
                auth=(username, password),
                files={'File': (os.path.basename(file), open(file))}).json()['id']

    # Poll until output is ready
    if file_id:
        print(file_id)
        wait = 20
        while wait > 0:
            status = requests.get(
                'http://' + dts + ':9000/api/extractions/' + file_id + '/status').json()
            if status['Status'] == 'Done':
                break
            time.sleep(1)
            wait -= 1

        # Display extracted content (TODO: needs to be one endpoint!!!)
        res = requests.get(
            'http://' + dts + ':9000/api/files/' + file_id + '/metadata.jsonld')
        print(res.text)
        metadata = res.json()

    return metadata

if __name__ == "__main__":
    main()
