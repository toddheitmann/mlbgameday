"""
This module is for database functions with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""
import sys
from os.path import isfile, dirname, join, exists
import datetime as dt
import time
from multiprocessing import Pool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
import pandas as pd

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

def get_game_models(game_date):
    objects = []
    games = download.get_games(game_date)
    for game in games:
        objects.append(models.Game(**game))
        players = parse.get_players(game['gid'], game['game_pk'], game['game_date'])
        for player in players['players']:
            objects.append(models.Player(**player))
        for coach in players['coaches']:
            objects.append(models.Coach(**coach))
        for umpire in players['umpires']:
            objects.append(models.Umpire(**umpire))
        events = parse.get_events(game['gid'], game['game_pk'], game['venue_id'], game_date)
        for event in events:
            pitches = event.pop('pitches', None)
            if pitches is not None:
                for pitch in pitches:
                    objects.append(models.Pitch(**pitch))
            runners = event.pop('runners', None)
            if runners is not None:
                for runner in runners:
                    objects.append(models.Runner(**runner))
            pickoffs = event.pop('pickoffs', None)
            if pickoffs is not None:
                for pickoff in pickoffs:
                    objects.append(models.Pickoff(**pickoff))
            if event['event_type'] == 'atbat':
                event.pop('event_type', None)
                objects.append(models.AtBat(**event))
            elif event['event_type'] == 'action':
                event.pop('event_type', None)
                objects.append(models.Action(**event))
    return objects

def update_db():
    session = get_session()
    last_game_date = session.query(models.Game.game_date).\
                     order_by(models.Game.game_date.desc()).first()

    if last_game_date is not None:
        last_game_date = last_game_date[0]
    else:
        last_game_date = dt.date(2010,1,1)

    # download.update_all(start_date = last_game_date)

    ### upsert possible exisiting data ###
    last_game_date_objects = get_game_models(last_game_date)

    ### increment to day not in database and bulk insert ###
    last_game_date = last_game_date + dt.timedelta(days = 1)

    for d in range((dt.date.today() - last_game_date).days):
        game_date = last_game_date + dt.timedelta(d)
        objects = get_game_models(game_date)
        session.bulk_save_objects(objects)
        session.commit()
    session.close()

class MLBQuery(Query):

    def __init__(self, *args, **kwargs):
        Query.__init__(self, *args, session = create_session(), **kwargs)

    def frame(self):
        """Return PANDAS DataFrame"""
        df = pd.read_sql(self.statement, self.session.bind)
        self.session.close()
        return df

if __name__ == "__main__":
    start = time.time()
    update_db()
    run_time = (time.time() - start) / 3600.0
    print("--- %.2f hours ---" % run_time)
