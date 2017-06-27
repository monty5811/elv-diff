from datetime import datetime as dt
from os.path import dirname, join

from dotenv import load_dotenv


def _load_dot_env():
    """Load config values from `.env`."""
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)


def to_epoch(t):
    """Convert time from Elvanto into Epoch time for slack."""
    return dt.strptime(t, '%Y-%m-%d %H:%M:%S').strftime('%s')
