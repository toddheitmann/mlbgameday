from sqlalchemy.orm.query import Query

import settings
from models import *


def db_create():
    """Creates tables for the database"""
    Base.metadata.create_all(engine)

class Connection(object):
    """Database Connection Object"""
    def __init__(self):
        """Initializes database connection and sessionmaker"""
        engine = create_engine(URL(**settings.DATABASE))
        self.Session = sessionmaker(bind=engine)

    def insert(self, obj):
        """Saves the object to the database"""
        session = self.Session()
        try:
            session.add(obj)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return obj

class Game(Query):
    """Game Table Object"""
    def __init__(self, columns = []):
        """Returns Query of Game table"""
        engine = create_engine(URL(**settings.DATABASE))
        Session = sessionmaker(bind = engine)
        if len(columns > 0):
            test = 'query with specified columns'
        else:
            super(WellModel, session = Session())

    def frame():
        """returns query object as pandas dataframe"""
        return False
