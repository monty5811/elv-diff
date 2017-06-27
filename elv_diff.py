#!/usr/bin/env python
import logging
import os
import sys

from opbeat import Client
from opbeat.handlers.logging import OpbeatHandler

from diffing import run_diff, run_diff_groups
from elvanto import pull_groups, pull_people
from slack import post_to_slack
from storage import JsonFile, Mongo, StorageException
from utils import _load_dot_env

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format='[%(levelname)s] %(asctime)s - %(message)s'
)


def add_opbeat():
    """Add opbeat logging."""
    if os.environ.get('OPBEAT_ORGANIZATION_ID', None) is not None:
        client = Client()
        handler = OpbeatHandler(client)
        logger = logging.getLogger()
        logger.addHandler(handler)


def diff_people(old_ppl, new_ppl):
    """Check people for changes."""
    for result in run_diff(old_ppl, new_ppl):
        try:
            post_to_slack(result)
        except Exception as e:
            logging.exception('Issue posting to Slack')


def diff_groups(old_groups, new_groups, ppl):
    """Check groups for changes."""
    for result in run_diff_groups(old_groups, new_groups, ppl):
        try:
            post_to_slack(result)
        except Exception as e:
            logging.exception('Issue posting to slack')


def main():
    """
    Run the diffing.

    We:
        - load the new data from the network
        - load the old data from disk
        - save the new data to disk (becomes the old data next time)
        - compare the old and new and send any changes to slack
    """
    _load_dot_env()
    add_opbeat()
    new_ppl = pull_people()
    new_groups = pull_groups()
    if os.environ['MONGO_URL']:
        store = Mongo()
    else:
        store = JsonFile()
    try:
        old_ppl = store.load_people()
        store.save_people(new_ppl)
        diff_people(old_ppl, new_ppl)
    except StorageException:
        logging.info('No old people found, assuming first run.')
        store.save_people(new_ppl)
        exit()

    try:
        old_grps = store.load_groups()
        store.save_groups(new_groups)
        diff_groups(old_grps, new_groups, new_ppl)
    except StorageException:
        logging.info('No old groups found, assuming first run.')
        store.save_groups(new_groups)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.error('Check failed', exc_info=True)
