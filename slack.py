import os

import requests


SESSION = requests.Session()


def post_to_slack(diff_obj):
    """
    Send change to slack channel.

    diff_obj: Dict with changes
    formatter: Function to turn `diff_obj` into required slack format
    """
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    resp = SESSION.post(os.environ.get('SLACK_URL'), json=diff_obj.slack_format(), headers=headers)
    resp.raise_for_status()
