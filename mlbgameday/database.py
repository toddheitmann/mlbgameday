"""
This module is for database functions with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""
from os import makedirs
from os.path import isfile, dirname, join, exists, isdir
import datetime as dt
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.url import URL
import pandas as pd
import numpy as np

import download
import parse
import settings
import models

def get_engine():
    if settings.DATABASE['drivername'] == 'sqlite':
        db_file = join(dirname(__file__),'data','mlbgameday.sqlite')
        engine = create_engine('sqlite:///' + db_file)
        if not isfile(db_file):
            models.create_db(engine)
    else:
        engine = create_engine(URL(**settings.DATABASE))
    return engine

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind = engine)
    return Session()

class MLBQuery(Query):

    def __init__(self, *args, **kwargs):
        Query.__init__(self, *args, session = get_session(), **kwargs)

    def frame(self):
        """Return PANDAS DataFrame"""
        df = pd.read_sql(self.statement, self.session.bind)
        self.session.close()
        return df
