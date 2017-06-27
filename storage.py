import json
import logging
import os


logger = logging.getLogger()


class StorageException(Exception):
    pass


class JsonFile():
    """Use json files on disk for storage."""

    def __init__(self):
        """Define file names."""
        self.people_file = '.old.json'
        self.groups_file = '.old.groups.json'

    @staticmethod
    def _load_old_data(name):
        """Load data from disk."""
        with open(name, 'r') as _f:
            return json.loads(_f.read())

    @staticmethod
    def _save_new_data(data, name):
        """Save data to disk."""
        with open(name, 'w') as _f:
            _f.write(json.dumps(data))

    def load_people(self):
        """Load old people."""
        try:
            return self._load_old_data(self.people_file)
        except FileNotFoundError:
            raise StorageException('File not found')

    def save_people(self, data):
        """Save new people."""
        self._save_new_data(data, self.people_file)

    def load_groups(self):
        """Load old groups."""
        try:
            return self._load_old_data(self.groups_file)
        except FileNotFoundError:
            raise StorageException('File not found')

    def save_groups(self, data):
        """Save new groups."""
        self._save_new_data(data, self.groups_file)


class Mongo():

    def __init__(self):
        url = os.environ.get('MONGO_URL', None)
        if url is None:
            raise StorageException('No Mongo Url found')

        from pymongo import MongoClient
        client = MongoClient(url)
        db = client.elv_diff
        self._get_or_create_collection(db)

    def _get_or_create_collection(self, db):
        existing_collections = db.collection_names()
        if 'people' not in existing_collections:
            print('Creating people collection')
            db.create_collection('people', capped=True, max=1, size=2e8)
        if 'groups' not in existing_collections:
            print('Creating groups collection')
            db.create_collection('groups', capped=True, max=1, size=2e8)

        self.groups = db.groups
        self.people = db.people

    def load_people(self):
        people = self.people.find_one()
        if people is None:
            raise StorageException('People not found in mongo db')
        del people['_id']
        return people

    def save_people(self, data):
        self.people.insert_one(data)
        del data['_id']

    def load_groups(self):
        groups = self.groups.find_one()
        if groups is None:
            raise StorageException('Groups not found in mongo db')
        del groups['_id']
        return groups

    def save_groups(self, data):
        self.groups.insert_one(data)
        del data['_id']
