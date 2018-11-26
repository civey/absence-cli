#!/usr/bin/env python3
import argparse
import configparser
import getpass
import json
from datetime import datetime

import keyring
import requests
from mohawk import Sender

config = configparser.ConfigParser(
    interpolation=configparser.BasicInterpolation())
config.read('config.ini')

user_id = config['ABSENCE']['user_id']

key = keyring.get_password('Absence.io', user_id)

if key is None:
    keyring.set_password("Absence.io", user_id, getpass.getpass())
    key = keyring.get_password('Absence.io', user_id)


def now_string():
    (dt, micro) = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f").split('.')
    return "%s.%03dZ" % (dt, int(micro) / 1000)


def start():
    entry = {
        "userId": user_id,
        "start": now_string(),
        "end": None,
        "timezoneName": "CET",
        "timezone": "+0100",
        "type": "work"
    }

    url = 'https://app.absence.io/api/v2/timespans/create'
    method = 'POST'
    content = json.dumps(entry)

    content_type = 'application/json'

    sender = Sender({'id': user_id,
                     'key': key,
                     'algorithm': 'sha256'},
                    url,
                    method,
                    content=content,
                    content_type=content_type)
    response = requests.post(url, data=content, headers={
                             'Authorization': sender.request_header, 'Content-Type': content_type})
    return response


def stop():
    entry = {
        "filter": {
            "userId": user_id,
            "end": {"$eq": None}
        },
        "limit": 10,
        "skip": 0
    }

    url = 'https://app.absence.io/api/v2/timespans'
    method = 'POST'
    content = json.dumps(entry)

    content_type = 'application/json'

    sender = Sender({'id': user_id,
                     'key': key,
                     'algorithm': 'sha256'},
                    url,
                    method,
                    content=content,
                    content_type=content_type)
    response = requests.post(url, data=content, headers={
                             'Authorization': sender.request_header, 'Content-Type': content_type})
    if response.ok:
        response = json.loads(response.text)
        existing_entry = response['data'][0]
    else:
        return None

    entry = {
        "start": existing_entry['start'],
        "end": now_string(),
        "timezoneName": "CET",
        "timezone": "+0100"
    }

    url = 'https://app.absence.io/api/v2/timespans/{}'.format(
        existing_entry['_id'])
    method = 'PUT'
    content = json.dumps(entry)

    content_type = 'application/json'

    sender = Sender({'id': user_id,
                     'key': key,
                     'algorithm': 'sha256'},
                    url,
                    method,
                    content=content,
                    content_type=content_type)
    response = requests.put(url, data=content, headers={
                            'Authorization': sender.request_header, 'Content-Type': content_type})
    return response


actions = {'start': start,
           'stop': stop}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get you some polls')
    parser.add_argument('action',
                        help='What to do'
                        )

    args = parser.parse_args()
    response = actions[args.action]()
    if response is not None and response.ok:
        print('Success')
