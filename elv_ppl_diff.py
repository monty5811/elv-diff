#!/usr/bin/env python
import json
import logging

from diffing import run_diff
from elvanto import pull_people
from slack import post_to_slack
from utils import _load_dot_env

logging.basicConfig(
    filename='elv_ppl_diff.log',
    level=logging.WARNING,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)


def load_old_data():
    with open('.old.json', 'r') as f:
        return json.loads(f.read())


def save_new_data(data):
    with open('.old.json', 'w') as f:
        f.write(json.dumps(data))


if __name__ == '__main__':
    _load_dot_env()
    new_data = pull_people()
    try:
        old_data = load_old_data()
    except FileNotFoundError:
        logging.warning('No .old.json found, assuming first run.')
        save_new_data()
        exit()

    d = run_diff(old_data, new_data)
    if not d:
        logging.warning('No change to data.')
        exit()

    for x in d:
        try:
            post_to_slack(x)
        except Exception as e:
            logging.exception('Exception posting to Slack')

    save_new_data(new_data)
