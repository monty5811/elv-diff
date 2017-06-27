import json
import os

import requests

people_fields = [
    'gender',
    'birthday',
    'anniversary',
    'school_grade',
    'marital_status',
    'security_code',
    'receipt_name',
    'giving_number',
    'mailing_address',
    'mailing_address2',
    'mailing_city',
    'mailing_state',
    'mailing_postcode',
    'mailing_country',
    'home_address',
    'home_address2',
    'home_city',
    'home_state',
    'home_postcode',
    'home_country',
    'reports_to',
    # the following array fields are not handled nicely
    # 'access_permissions',
    # 'departments',
    # 'service_types',
    # 'demographics',
    # 'locations',
    # 'family',
    # TODO handle custom fields
]

group_fields = [
    'people',
    # 'categories',
    # 'departments',
    # 'demographics',
    # 'locations',
]


class ElvantoApiException(Exception):
    """Generic Elvanto Exception."""

    pass


s = requests.Session()


def retry_request(url, http_method, *args, **kwargs):
    """Retry failed requests 3 times."""
    assert http_method in ['get', 'post', 'delete', 'patch', 'put']
    MAX_TRIES = 3
    r_func = getattr(s, http_method)
    tries = 0
    while True:
        resp = r_func(url, *args, **kwargs)
        if resp.status_code != 200 and tries < MAX_TRIES:
            tries += 1
            continue
        break

    return resp


def e_api(end_point, **kwargs):
    """Elvanto api client."""
    ELVANTO_KEY = os.environ.get('ELVANTO_KEY')
    base_url = 'https://api.elvanto.com/v1/'
    e_url = '{0}{1}.json'.format(base_url, end_point)
    resp = retry_request(e_url, 'post', json=kwargs, auth=(ELVANTO_KEY, '_'))
    data = json.loads(resp.text)
    if data['status'] == 'ok':
        return data
    else:
        raise ElvantoApiException(data['error'])


def pull_data(name, end_point, fields, ident):
    """Page through elvanto resource."""
    page = 1
    data = e_api(
        end_point,
        page_size=1000,
        fields=fields,
    )

    if data['status'] != 'ok':
        raise elvanto.ElvantoApiException

    items = data[name][ident]
    num_synced = data[name]['on_this_page']
    while num_synced < data[name]['total']:
        page += 1
        more_data = e_api(
            end_point,
            page=page,
            page_size=1000,
            fields=fields,
        )
        items += more_data[name][ident]
        num_synced += more_data[name]['on_this_page']

    return {x['id']: x for x in items}


def pull_people():
    """Pull people from elvanto."""
    name = 'people'
    end_point = 'people/getAll'
    fields = people_fields
    ident = 'person'
    return pull_data(name, end_point, fields, ident)


def pull_groups():
    """Pull groups from elvanto."""
    name = 'groups'
    end_point = 'groups/getAll'
    fields = group_fields
    ident = 'group'
    return pull_data(name, end_point, fields, ident)
