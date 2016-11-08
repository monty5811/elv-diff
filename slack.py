import os

import requests

from utils import to_epoch


def format_message(d):
    url = 'https://{0}/admin/people/person/?id={1}'.format(
        os.environ.get('ELVANTO_DOMAIN', ''), d['person']['id']
    )
    name = '{firstname} {lastname}\n'.format(**d['person'])
    msg = '{diff_path}:\n{old}->{new}'.format(**d)
    return {
        'username': os.environ.get('SLACK_USERNAME', 'elvanto-updates'),
        'channel': '#' + os.environ.get('SLACK_CHANNEL', 'elvanto-updates'),
        'attachments': [
            {
                'fallback': '{name}\n{msg}'.format(
                    name=name, msg=msg
                ),
                'color': '#36a64f',
                'author_name': name,
                'author_link': url,
                'thumb_url': d['person']['picture'],
                'text': d['diff_path'],
                'fields': [
                    {
                        'title': 'Old',
                        'value': d['old'],
                        'short': True,
                    },
                    {
                        'title': 'New',
                        'value': d['new'],
                        'short': True,
                    },
                ],
                'ts': to_epoch(d['person']['date_modified']),
            }
        ]
    }


def post_to_slack(diff_obj):
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(
        os.environ.get('SLACK_URL'),
        json=format_message(diff_obj),
        headers=headers
    )
    r.raise_for_status()
