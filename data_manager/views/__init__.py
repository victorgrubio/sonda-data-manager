'''
Created on 18 mar. 2020

@author: victor
'''
from .auth import auth as auth_view
from .db import db as db_view
from .documents import documents as documents_view
from .config import config as config_view
from .files import files as files_view
from .journeys import journeys as journeys_view
from .programs import programs as programs_view
from .search import search as search_view
from .probe import probe as probe_view
from .vod import vod as vod_view

from .anomalies import anomalies as anomalies_view