"""
This module updates data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
"""

import datetime as dt
import time
import pandas as pd
from sqlalchemy.orm import aliased
from sqlalchemy import update

import database
import download
import models
import parse
import settings

def update_gameday(delete_files = False):

    session = database.get_session()
    print('Downloading MLBGameDay Data')
    last_game_date = session.query(models.Game.game_date).\
                     order_by(models.Game.game_date.desc()).first()

    if last_game_date is not None:
        last_game_date = last_game_date[0] + dt.timedelta(days = 1)
    else:
        last_game_date = dt.date(2010,1,1)
    last_game_date = dt.date(2016, 1,1) # debugging and testing

    download.update_xml(start_date = last_game_date)

    update_year = last_game_date.year
    print('Processing MLBGameDay for year %i.' % update_year)
    for d in range((dt.date.today() - last_game_date).days):
        game_date = last_game_date + dt.timedelta(d)
        if game_date.year != update_year:
            update_year = game_date.year
            print('Processing MLBGameDay for year %i.' % update_year)

        objects = parse.get_game_models(game_date)
        session.bulk_save_objects(objects)
        session.commit()
    session.close()

    # if delete_files:
    #     download.remove_mlbam_downloads()

def update_trajectory():

    engine = database.get_engine()
    session = database.get_session()

    last_trajectory_date = session.query(models.Trajectory.game_date).\
                   order_by(models.Trajectory.game_date.desc()).first()

    if last_trajectory_date is not None:
        trajectory_start_year = last_trajectory_date[0].year
        session.query(models.Trajectory).filter(models.Trajectory.game_date >= \
                  dt.date(trajectory_start_year, 1, 1)).delete()
        session.commit()
    else:
        trajectory_start_year = 2015
    # trajectory_start_year = 2016 # debugging and testing
    session.close()

    print('Downloading Trajectory Data')
    download.download_trajectory_csvs(start_year = trajectory_start_year, overwrite = True)

    print('Processing Trajectory Data')
    for year in range(trajectory_start_year, dt.date.today().year + 1):
        df = parse.get_trajectory_df(year)
        df.to_sql('trajectory', engine, if_exists = 'append', index = False)

    download.remove_trajectory_downloads()


def update_retrosheet():

    engine = database.get_engine()
    session = database.get_session()

    print('Downloading Retrosheet Data')
    last_retro_date = session.query(models.Event.game_date).\
                      order_by(models.Event.game_date.desc()).first()

    if last_retro_date is not None:
        retro_start_year = last_retro_date[0].year + 1
    else:
        retro_start_year = 1871
    # retro_start_year = 2016 # debugging and testing
    download.download_retrosheet(start_year = retro_start_year)

    print('Processing Retrosheet Data')
    years = []
    for year in range(retro_start_year, dt.date.today().year + 1):
        df = parse.get_game_log_df(year)
        df.to_sql('game_log', engine, if_exists = 'append', index = False)

        if year > 1920:
            df = parse.get_retro_subs_df(year)
            df.to_sql('sub', engine, if_exists = 'append', index = False)

            df = parse.get_retro_event_df(year)
            df.to_sql('event', engine, if_exists = 'append', index = False)

    print('Processing Lookup Data')
    teams = parse.get_team_df()
    if len(teams) > 0:
        session.query(models.Team).delete()
        session.commit()
        teams.to_sql('team', engine, if_exists = 'append', index = False)

    people = parse.get_person_df()
    if len(people) > 0:
        session.query(models.Person).delete()
        session.commit()
        people.to_sql('person', engine, if_exists = 'append', index = False)

    park = parse.get_park_df()
    if len(park) > 0:
        session.query(models.Park).delete()
        session.commit()
        park.to_sql('park', engine, if_exists = 'append', index = False)

    session.close()

    download.remove_retrosheet_downloads()

def update_weather():

    parse.get_weather_data()

    engine = database.get_engine()
    session = database.get_session()

    gids = session.query(models.Game.gid).filter\
            (models.Trajectory.temperature == None, models.Game.game_pk == models.Trajectory.game_pk).all()

    gids += session.query(models.HIP.gid).filter(models.HIP.temperature == None).all()

    data_models = [models.AtBat, models.Action, models.Pitch]
    for m in data_models:
        gids += session.query(m.gid).filter(m.temperature == None).all()
    gids = list(set(gids))

    for gid in gids:
        gid = gid[0]

        weather = session.query(models.Weather).filter(models.Weather.gid == gid)
        weather = pd.read_sql(weather.statement, weather.session.bind)

        date_times = []
        for m in data_models:
            date_times += session.query(m.datetime).filter((m.temperature == None) & (m.gid == gid)).all()

        weather = weather.append(pd.DataFrame(date_times), ignore_index = True)
        weather = weather.sort_values(by = 'datetime').set_index('datetime')
        weather = weather.interpolate(method = 'time')
        weather = weather.reset_index()

        weather_columns = ['temperature', 'heat_index', 'dew_point', 'humidity', 'pressure', 'visibility', 'wind_dir', 'wind_speed', 'gust_speed', 'precipitation']
        for m in data_models:
            model_objects = session.query(m).filter((m.temperature == None) & (m.gid == gid)).all()
            for model in model_objects:
                row = weather[weather.datetime == model.datetime]
                if len(row) > 0:
                    row = row.iloc[0]
                    for column in weather_columns:
                        setattr(model, column, row[column])
        session.commit()


def update_event_keys():

    session = database.get_session()

    batter = aliased(models.Person, name = 'batter')
    pitcher = aliased(models.Person, name = 'pitcher')

    print('Adding retro_event keys to HIP')
    events = session.query(models.HIP, models.Event.event_id).\
                filter(models.HIP.pitcher == pitcher.key_mlbam).\
                filter(models.Event.pit_id == pitcher.key_retro).\
                filter(models.HIP.batter == batter.key_mlbam).\
                filter(models.Event.bat_id == batter.key_retro).\
                filter(models.HIP.retro_gid == models.Event.game_id).\
                filter(models.HIP.inning == models.Event.inn_ct).\
                filter(models.HIP.retro_event_id == None).all()
    for row in events:
        row[0].retro_event_id = row[1]
    session.commit()

    print('Adding retro_event keys to AtBat')
    events = session.query(models.AtBat, models.Event.event_id).\
                filter(models.AtBat.pitcher == pitcher.key_mlbam).\
                filter(models.Event.pit_id == pitcher.key_retro).\
                filter(models.AtBat.batter == batter.key_mlbam).\
                filter(models.Event.bat_id == batter.key_retro).\
                filter(models.AtBat.retro_gid == models.Event.game_id).\
                filter(models.AtBat.inning == models.Event.inn_ct).\
                filter(models.AtBat.retro_event_id == None).limit(1000).all()

    for row in events:
        row[0].retro_event_id = row[1]
    session.commit()

    print('Adding retro_event keys to Pitch')
    events = session.query(models.Pitch, models.Event.event_id).\
                filter(models.Pitch.pitcher == pitcher.key_mlbam).\
                filter(models.Event.pit_id == pitcher.key_retro).\
                filter(models.Pitch.batter == batter.key_mlbam).\
                filter(models.Event.bat_id == batter.key_retro).\
                filter(models.Pitch.retro_gid == models.Event.game_id).\
                filter(models.Pitch.inning == models.Event.inn_ct).\
                filter(models.Pitch.retro_event_id == None).limit(1000)

    events = events.all()

    for row in events:
        row[0].retro_event_id = row[1]
    session.commit()

    print('Adding retro_gid keys to Trajectory')
    games = session.query(models.Trajectory, models.Game.retro_gid).\
                filter(models.Trajectory.game_pk == models.Game.game_pk).\
                filter(models.Trajectory.retro_gid == None).limit(1000).all()

    for row in games:
        row[0].retro_gid = row[1]
    session.commit()

    print('Adding retro_event keys to Trajectory')
    events = session.query(models.Trajectory, models.Event.event_id).\
                filter(models.Trajectory.pitcher == pitcher.key_mlbam).\
                filter(models.Event.pit_id == pitcher.key_retro).\
                filter(models.Trajectory.batter == batter.key_mlbam).\
                filter(models.Event.bat_id == batter.key_retro).\
                filter(models.Trajectory.retro_gid == models.Event.game_id).\
                filter(models.Trajectory.inning == models.Event.inn_ct).\
                filter(models.Trajectory.retro_event_id == None).limit(1000).all()

    for row in events:
        row[0].retro_event_id = row[1]
    session.commit()

    session.close()

def update(delete_files = False):

    update_gameday(delete_files = delete_files)

    update_trajectory()

    update_retrosheet()

    update_event_keys()

    update_weather()

if __name__ == "__main__":
    start = time.time()
    update()
    run_time = (time.time() - start) / 3600.0
    print("--- %.2f hours ---" % run_time)
