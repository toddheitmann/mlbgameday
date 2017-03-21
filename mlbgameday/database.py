"""
This module is for database functions with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

from os.path import isfile, dirname, join, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query

import settings
import models

import pandas as pd


def create_session():
    if settings.DATABASE['drivername'] == 'sqlite':
        db_file = join(dirname(__file__),'data', 'mlbgameday.sqlite')
        engine = create_engine('sqlite:////' + db_file)
        if not isfile(db_file):
            models.create_db(engine)
    else:
        engine = create_engine(URL(**settings.DATABSAE))
    Session = sessionmaker(bind = engine)
    return Session()

class MLBQuery(Query):

    def __init__(self, *args, **kwargs):
        session = create_session()
        Query.__init__(self, *args, **kwargs, session = session)

    def frame(self):
        """Return PANDAS DataFrame"""
        return pd.read_sql(self.statement, self.session.bind)
