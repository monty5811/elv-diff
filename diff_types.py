import os
from utils import to_epoch


class BaseDiff():
    """Base class for different elvanto types that we diff."""

    def __init__(self, path="", item="", old=None, new=None):
        """Create class from data."""
        self.path = path
        self.item = item
        self.old = old
        self.new = new

    @property
    def url(self):
        """
        Return the url to the changed resource.

        This needs to be implemented for each resource type.
        """
        raise NotImplementedError

    @property
    def name(self):
        """Name of resource."""
        return self.item['name']

    @property
    def fallback_message(self):
        """Fallback message for slack."""
        if self.old is None and self.new is None:
            msg = f'{self.path}'
        else:
            msg = f'{self.path}:\n{self.old}->{self.new}'
        return f'{self.name}\n{msg}'

    def slack_format(self):
        """Build output to be sent to slack."""
        fields = []
        if self.old is not None:
            fields.append({
                'title': 'Old',
                'value': self.old,
                'short': True,
            })
        if self.new is not None:
            fields.append({
                'title': 'New',
                'value': self.new,
                'short': True,
            })
        return {
            'username': os.environ.get('SLACK_USERNAME', 'elvanto-updates'),
            'channel': '#' + os.environ.get('SLACK_CHANNEL', 'elvanto-updates'),
            'attachments': [
                {
                    'fallback': self.fallback_message,
                    'color': '#36a64f',
                    'author_name': self.name,
                    'author_link': self.url,
                    'thumb_url': self.item['picture'],
                    'text': self.path,
                    'fields': fields,
                    'ts': to_epoch(self.item['date_modified']),
                }
            ]
        }


class GroupDiff(BaseDiff):
    """Group change."""

    @property
    def url(self):
        """Url for changed group."""
        domain = os.environ.get('ELVANTO_DOMAIN', '')
        return f'https://{domain}/admin/groups/group/?id={self.item["id"]}'


class PersonDiff(BaseDiff):
    """Person change."""

    @property
    def url(self):
        """Url for changed person."""
        domain = os.environ.get('ELVANTO_DOMAIN', '')
        return f'https://{domain}/admin/people/person/?id={self.item["id"]}'

    @property
    def name(self):
        """Name of resource."""
        return f'{self.item["firstname"]} {self.item["lastname"]}'
