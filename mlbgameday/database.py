"""
This module is for database functions with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""
from os import makedirs
from os.path import isfile, dirname, join, exists, isdir
import platform
import subprocess
import datetime as dt
import time
from zipfile import ZipFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
import pandas as pd
from io import BytesIO

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

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
        hips = parse.get_hip(game['gid'], game['game_pk'], game['venue_id'])
        for hip in hips:
            objects.append(models.HIP(**hip))
    return objects

def update_db():
    session = get_session()
    last_game_date = session.query(models.Game.game_date).\
                     order_by(models.Game.game_date.desc()).first()

    if last_game_date is not None:
        last_game_date = last_game_date[0]
        retro_start_year = last_game_date.year
    else:
        last_game_date = dt.date(2010,1,1)
        retro_start_year = 1871

    # download.update_all(start_date = last_game_date)

    ### upsert possible exisiting data ###
    last_game_date_objects = get_game_models(last_game_date)
    if len(last_game_date_objects) > 0:
        session.bulk_save_objects(last_game_date_objects)
        session.commit()

    ### increment to day not in database and bulk insert ###
    last_game_date = last_game_date + dt.timedelta(days = 1)

    update_year = last_game_date.year
    print('Processing MLB data for %i.' % update_year)
    for d in range((dt.date.today() - last_game_date).days):
        game_date = last_game_date + dt.timedelta(d)
        if game_date.year != update_year:
            update_year = game_date.year
            print('Processing MLB data for %i.' % update_year)

        objects = get_game_models(game_date)
        session.bulk_save_objects(objects)
        session.commit()
    session.close()

    ### update retrosheet data ###

    ### download and unzip retrosheet files ###
    print('Downloading Retrosheet Event Data.')
    raw_dir = join(dirname(__file__), 'data')
    for i in range(retro_start_year, dt.date.today().year + 1):
        ### download gamee files ###
        url_format = "http://www.retrosheet.org/gamelogs/gl%i.zip" % i
        try:
            url = urlopen(url_format)
            zipfile = ZipFile(BytesIO(url.read()))
            save_dir = join(raw_dir, 'gamelogs')
            if not isdir(save_dir):
                makedirs(save_dir)
            zipfile.extractall(save_dir)
        except:
            ### year does not contain event files ###
            do = 'nothing'

        ## download event files after 1920 ###
        if i > 1920:
            url_format = "http://www.retrosheet.org/events/%ieve.zip" % i
            try:
                url = urlopen(url_format)
                zipfile = ZipFile(BytesIO(url.read()))
                save_dir = join(raw_dir, 'event', str(i))
                if not isdir(save_dir):
                    makedirs(save_dir)
                zipfile.extractall(save_dir)
            except:
                ### year does not contain event files ###
                do = 'nothing'

    ### process files through chadwick ###
    system = platform.system()
    if system == 'Windows':
        event_exe = join(dirname(__file__), 'exe', 'cwevent.exe')
        sub_exe = join(dirname(__file__), 'exe', 'cwsub.exe')
    elif system == 'Darwin':
        event_exe = 'cwevent'
        sub_exe = 'cwsub'
    elif system == 'Linux':
        event_exe = None
        sub_exe = None
    else:
        raise ValueError('Cannot find system platform')

    years = []
    db_engine = get_engine()
    for i in range(retro_start_year, dt.date.today().year + 1):
        year = str(i)
        ### process game files ###
        # gl_file = join(raw_dir, 'gamelogs', 'GL' + year + '.txt')
        # if isfile(gl_file):
        #     df = pd.read_csv(gl_file)

        if i > 1920:
            working_dir = join(raw_dir, 'event', year)
            if isdir(working_dir):
                ### process event ###
                args  = ' -f 0-96 -x 0-60 -n -y %s *.EV*' % year
                cmd = event_exe + args
                output = subprocess.check_output(args = cmd, cwd = working_dir, shell = True)
                df = pd.read_csv(BytesIO(output), low_memory = False)
                column_names = []
                for c in df.columns.values:
                    column_names.append(c.lower())
                df.columns = column_names
                df.to_sql('event', db_engine, if_exists = 'append', index = False)

                ### process sub ###
                args = ' -n -y %s *.EV*' % year
                cmd = sub_exe + args
                output = subprocess.check_output(args = cmd, cwd = working_dir, shell = True)
                df = pd.read_csv(BytesIO(output), low_memory = False)
                column_names = []
                for c in df.columns.values:
                    column_names.append(c.lower())
                df.columns = column_names
                df.to_sql('sub', db_engine, if_exists = 'append', index = False)

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
