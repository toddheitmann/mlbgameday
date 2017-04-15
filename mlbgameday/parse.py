"""
This module parses individual game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

import gzip
from os import listdir
from os.path import isfile, isdir, join, dirname
import datetime as dt
import xml.etree.ElementTree as ET
import pandas as pd
from io import BytesIO
import platform
import subprocess
import re

import constants
import database
import download
import models

def get_players(gid, retro_gid, game_pk, game_date):
    data = download.download_gid_file(gid, 'players.xml')
    root = ET.fromstring(data)
    players = []
    coaches = []
    umpires = []
    for elem in root:
        if elem.tag == 'team':
            if elem.attrib['type'] == 'home':
                home_flag = 1
            else:
                home_flag = 0
            player_nodes = elem.findall('player')
            if player_nodes is not None:
                for person in player_nodes:
                    player = {'gid': gid, 'retro_gid': retro_gid, 'game_pk': game_pk, 'home_flag': home_flag, 'game_date': game_date}
                    player = download.get_attributes(player, person, 'player')
                    # if len(player['first']) < 1:
                    #     # mlb errors for player allocation at games example:
                    #     # http://gd2.mlb.com/components/game/mlb/year_2010/
                    #     # month_03/day_13/gid_2010_03_13_minmlb_phimlb_1/players.xml
                    #     continue
                    players.append(player)
            coach_nodes = elem.findall('coach')
            if coach_nodes is not None:
                for person in coach_nodes:
                    coach = {'gid': gid, 'retro_gid': retro_gid, 'game_pk': game_pk, 'home_flag': home_flag, 'game_date': game_date}
                    coach = download.get_attributes(coach, person, 'coach')
                    coaches.append(coach)
        elif elem.tag == 'umpires':
            umpire_nodes = elem.findall('umpire')
            if umpire_nodes is not None:
                for person in umpire_nodes:
                    umpire = {'gid': gid, 'retro_gid': retro_gid, 'game_pk': game_pk, 'game_date': game_date}
                    umpire = download.get_attributes(umpire, person, 'umpire')
                    umpires.append(umpire)
    return {'players': players, 'coaches': coaches, 'umpires': umpires}

def get_hip(gid, retro_gid, game_date, game_pk, venue_id):
    data = download.download_gid_file(gid, 'inning_hip.xml')
    root = ET.fromstring(data)
    hips = []
    hip_nodes = root.findall('hip')
    for node in hip_nodes:
        hip = {'gid': gid, 'retro_gid': retro_gid, 'game_date': game_date, 'game_pk': game_pk, 'venue_id': venue_id}
        hip = download.get_attributes(hip, node, 'hip')
        hips.append(hip)
    return hips

def get_base_state(bases):
    """Returns string base state from bases dictionary"""
    if bases['1B'] is not None:
        if bases['2B'] is not None:
            if bases['3B'] is not None:
                base_state = '123'
            else:
                base_state = '120'
        else:
            if bases['3B'] is not None:
                base_state = '103'
            else:
                base_state = '100'
    else:
        if bases['2B'] is not None:
            if bases['3B'] is not None:
                base_state = '023'
            else:
                base_state = '020'
        else:
            if bases['3B'] is not None:
                base_state = '003'
            else:
                base_state = '000'
    return base_state

def get_events(gid, retro_gid, game_pk, venue_id, game_date):
    """Returns event dictionary list for specificed game and venue"""

    ### setup game variables ###
    halves = {'top': 'top', 'bottom': 'bot'}
    bases = {'1B': None, '2B': None, '3B': None, '': None}
    runs = {'home_team_runs': 0, 'away_team_runs': 0}
    players = get_players(gid, retro_gid, game_pk, game_date)
    for umpire in players['umpires']:
        if umpire['position'] == 'home':
            home_umpire = umpire['umpire_id']

    catcher = {'top': None, 'bot': None}
    for player in players['players']:
        if 'current_position' in player:
            if player['current_position'] == 'C':
                if player['home_flag'] == 1:
                    catcher['bot'] = player['player_id']
                elif player['home_flag'] == 0:
                    catcher['top'] = player['player_id']

    ### get inning_all data ###
    data = download.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    innings = root.findall('inning')

    ### beging traversing xml file ###
    events = []
    game_event_number = 1
    game_pitch_count = 1
    game_runner_count = 1
    game_pickofff_count = 1
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            outs = 0
            inning_topbot = halves[half]
            inning_node = inning.find(half)
            if inning_node is not None:
                for node in inning_node:
                    event = {'gid': gid, 'retro_gid': retro_gid, 'game_date': game_date, 'game_pk': game_pk, 'venue_id': venue_id, 'inning_topbot': inning_topbot, 'inning': inning_number, 'game_event_number': game_event_number, 'umpire': home_umpire, 'catcher': catcher[inning_topbot] ,'start_outs': outs}
                    base_state = get_base_state(bases)
                    event['start_base_state'] = base_state
                    event['start_out_base_state'] = str(outs) + base_state
                    for base in bases:
                        event['start_' + base] = bases[base]
                    for run in runs:
                        event['start_' + run] = runs[run]
                    event.pop('start_', None)

                    if node.tag == 'atbat':
                        ### parse atbat node ###
                        atbat = dict(event)
                        atbat['event_type'] = 'atbat'
                        atbat = download.get_attributes(atbat, node, 'atbat')
                        event['pitcher'] = atbat['pitcher']
                        event['batter'] = atbat['batter']

                        ### parse atbat children ###
                        pitches = []
                        pickoffs = []
                        runners = []
                        for c, child in enumerate(node):
                            if child.tag == 'pitch':
                                ### parse pitch node ###
                                pitch = dict(event)
                                pitch['game_pitch_count'] = game_pitch_count
                                pitch = download.get_attributes(pitch, child, 'pitch')
                                ### add base state ###
                                base_state = get_base_state(bases)
                                for base in bases:
                                    pitch['start_' + base] = bases[base]
                                    pitch['start_base_state'] = base_state
                                for run in runs:
                                    pitch['start_' + run] = runs[run]
                                pitches.append(pitch)
                                game_pitch_count += 1

                            elif child.tag == 'runner':
                                ### parse runner node ###
                                runner = dict(event)
                                runner['game_runner_count'] = game_runner_count
                                runner = download.get_attributes(runner, child, 'runner')

                                ### adjust changing base state ###
                                if c + 1 == len(node):
                                    ### occurs at this atbat ###
                                    bases[runner['start']] = None
                                    bases[runner['end']] = runner['runner_id']
                                else:
                                    if node[c + 1] == 'runner':
                                        ### occurs at this atbat ###
                                        bases[runner['start']] = None
                                        bases[runner['end']] = runner['runner_id']
                                    else:
                                        ### occurs at previous action node ###

                                        ### NEED TO ADJUST AT BAT OUTS FOR CAUGHT STEALING ###

                                        bases[runner['start']] = None
                                        bases[runner['end']] = runner['runner_id']
                                        atbat['start_' + runner['start']] = None
                                        atbat['start_' + runner['end']] = runner['runner_id']
                                        event['start_' + runner['start']] = None
                                        event['start_' + runner['end']] = runner['runner_id']
                                        events[-1]['end_' + runner['start']] = None
                                        events[-1]['end_' + runner['end']] = runner['runner_id']
                                        events[-1]['pitcher'] = atbat['pitcher']
                                        events[-1].pop('end_', None)
                                        if 'score' in runner:
                                            if atbat['inning_topbot'] == 'top':
                                                runs['away_team_runs'] += 1
                                                events[-1]['end_away_team_runs'] = runs['away_team_runs']
                                                event['start_away_team_runs'] = runs['away_team_runs']
                                                atbat['start_away_team_runs'] = runs['away_team_runs']
                                            else:
                                                runs['home_team_runs'] += 1
                                                events[-1]['end_home_team_runs'] = runs['home_team_runs']
                                                event['end_home_team_runs'] = runs['home_team_runs']
                                                atbat['start_away_team_runs'] = runs['away_team_runs']

                                ### add base state ###
                                base_state = get_base_state(bases)
                                for base in bases:
                                    runner['start_' + base] = bases[base]
                                    runner['start_base_state'] = base_state
                                for run in runs:
                                    runner['start_' + run] = runs[run]

                                runners.append(runner)
                                game_runner_count += 1

                            elif child.tag == 'po':
                                ### parse pickoff node ###
                                po = dict(event)
                                po['game_pickofff_count'] = game_pickofff_count
                                po = download.get_attributes(po, child, 'pickoff')

                                ### add base state ###
                                base_state = get_base_state(bases)
                                for base in bases:
                                    po['start_' + base] = bases[base]
                                    po['start_base_state'] = base_state
                                for run in runs:
                                    po['start_' + run] = runs[run]

                                pickoffs.append(po)
                                game_pickofff_count += 1

                            ### add final base states to child nodes ###
                            atbat['pitches'] = pitches
                            atbat['runners'] = runners
                            atbat['pickoffs'] = pickoffs

                            ### get run changes from event ###
                            for run in runs:
                                if run in event:
                                    runs[run] = atbat[run]
                            outs = atbat['o']

                            ### set end event values ###
                            base_state = get_base_state(bases)
                            out_base_state = str(outs) + base_state
                            atbat['end_base_state'] = base_state
                            atbat['end_out_base_state'] = out_base_state
                            for base in bases:
                                atbat['end_' + base] = bases[base]
                                for pitch in atbat['pitches']:
                                    pitch['end_' + base] = bases[base]
                                for runner in atbat['runners']:
                                    runner['end_' + base] = bases[base]
                                for po in atbat['pickoffs']:
                                    po['end_' + base] = bases[base]

                            for run in runs:
                                atbat['end_' + run] = runs[run]
                                atbat['end_outs'] = outs
                                for pitch in atbat['pitches']:
                                    pitch['end_' + run] = runs[run]
                                    pitch['end_base_state'] = base_state
                                    pitch['end_outs'] = outs
                                    pitch['end_out_base_state'] = out_base_state
                                    pitch.pop('start_', None)
                                    pitch.pop('end_', None)
                                for runner in atbat['runners']:
                                    runner['end_' + run] = runs[run]
                                    runner['end_base_state'] = base_state
                                    runner['end_outs'] = outs
                                    runner['end_out_base_state'] = out_base_state
                                    runner.pop('start_', None)
                                    runner.pop('end_', None)
                                for po in atbat['pickoffs']:
                                    po['end_' + run] = runs[run]
                                    po['end_base_state'] = base_state
                                    po['end_outs'] = outs
                                    po['end_out_base_state'] = out_base_state
                                    po.pop('start_', None)
                                    po.pop('end_', None)

                        atbat.pop('start_', None)
                        atbat.pop('end_', None)
                        atbat.pop('', None)
                        atbat.pop('home_team_runs', None)
                        atbat.pop('away_team_runs', None)
                        events.append(atbat)
                        game_event_number += 1

                    elif node.tag == 'action':
                        ### parse action node ###
                        action = dict(event)
                        action['event_type'] = 'action'
                        action = download.get_attributes(action, node, 'action')
                        base_state = get_base_state(bases)
                        action['end_outs'] = str(outs)
                        action['end_base_state'] = base_state
                        action['end_out_base_state'] = str(outs) + base_state
                        for base in bases:
                            action['end_' + base] = bases[base]
                        for run in runs:
                            action['end_' + run] = runs[run]
                        action.pop('end_', None)
                        events.append(action)
                        game_event_number += 1
    return events

def get_game_models(game_date):
    objects = []
    games = download.get_games(game_date)
    for game in games:
        objects.append(models.Game(**game))
        players = get_players(game['gid'], game['retro_gid'], game['game_pk'], game['game_date'])
        for player in players['players']:
            objects.append(models.Player(**player))
        for coach in players['coaches']:
            objects.append(models.Coach(**coach))
        for umpire in players['umpires']:
            objects.append(models.Umpire(**umpire))
        try:
            events = get_events(game['gid'], game['retro_gid'], game['game_pk'], game['venue_id'], game_date)
        except:
            events = []
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
        hips = get_hip(game['gid'], game['retro_gid'], game_date, game['game_pk'], game['venue_id'])
        for hip in hips:
            objects.append(models.HIP(**hip))
    return objects

def get_trajectory_df(year):
    """reads downloaded csv files into pandas dataframe"""
    ### get directory and files, iterate, read and apped to dataframe ###
    files_dir = join(dirname(__file__), 'data', 'trajectory', str(year))
    player_files = [f for f in listdir(files_dir) if isfile(join(files_dir, f))]
    df = pd.DataFrame()
    for file_name in player_files:
        file_path = join(files_dir, file_name)
        with gzip.open(file_path, 'r') as f:
            data = BytesIO(f.read())
        if len(data.getvalue()) > 0:
            df = df.append(pd.read_csv(data, parse_dates = ['game_date', 'tfs_zulu']))
    ### rename type to event_type ###
    column_names = df.columns.values
    for i, column in enumerate(column_names):
        if column == 'type':
            column_names[i] = 'event_type'
    df.columns = column_names
    df['px'] = pd.to_numeric(df.px, errors = 'coerce')
    df = df[df.game_pk.notnull()]
    df.drop_duplicates(inplace = True)
    return df

def get_game_log_df(year):

    columns = ['game_date', 'game_number', 'day', 'away_team_id', 'away_lg', 'away_game_number', 'home_team_id', 'home_lg', 'home_game_number', 'away_score_ct', 'home_score_ct', 'outs', 'daynight', 'completion', 'forfeit', 'protest', 'park', 'attendance', 'game_minutes', 'away_linescore', 'home_linescore', 'away_ab', 'away_h', 'away_2b', 'away_3b', 'away_hr', 'away_rbi', 'away_sh', 'away_sf', 'away_hbp', 'away_bb', 'away_ibb', 'away_so', 'away_sb', 'away_cs', 'away_gidp', 'away_ci', 'away_lob', 'away_pitchers_used', 'away_individual_er', 'away_team_er', 'away_wp', 'away_balks', 'away_putouts', 'away_assists', 'away_errors', 'away_passed_balls', 'away_double_plays', 'away_triple_plays', 'home_ab', 'home_h', 'home_2b', 'home_3b', 'home_hr', 'home_rbi', 'home_sh', 'home_sf', 'home_hbp', 'home_bb', 'home_ibb', 'home_so', 'home_sb', 'home_cs', 'home_gidp', 'home_ci', 'home_lob', 'home_pitchers_used', 'home_individual_er', 'home_team_er', 'home_wp', 'home_balks', 'home_putouts', 'home_assists', 'home_errors', 'home_passed_balls', 'home_double_plays', 'home_triple_plays', 'hp_ump_id', 'hp_ump_name', 'b1_ump_id', 'b1_ump_name', 'b2_ump_id', 'b2_ump_name', 'b3_ump_id', 'b3_ump_name', 'lf_ump_id', 'lf_ump_name', 'rf_ump_id', 'rf_ump_name', 'away_manager_id', 'away_manager_name', 'home_manager_id', 'home_manager_name', 'winning_pitcher_id', 'winning_pitcher_name', 'losing_pitcher_id', 'losing_pitcher_name', 'saving_pitcher_id', 'saving_pitcher_name', 'gwrbi_batter_id', 'gwrbi_batter_name', 'away_starting_pitcher_id', 'away_starting_pitcher_name', 'home_starting_pitcher_id', 'home_starting_pitcher_name', 'away_batter_1_id', 'away_batter_1_name', 'away_batter_1_pos', 'away_batter_2_id', 'away_batter_2_name', 'away_batter_2_pos', 'away_batter_3_id', 'away_batter_3_name', 'away_batter_3_pos', 'away_batter_4_id', 'away_batter_4_name', 'away_batter_4_pos', 'away_batter_5_id', 'away_batter_5_name', 'away_batter_5_pos', 'away_batter_6_id', 'away_batter_6_name', 'away_batter_6_pos', 'away_batter_7_id', 'away_batter_7_name', 'away_batter_7_pos', 'away_batter_8_id', 'away_batter_8_name', 'away_batter_8_pos', 'away_batter_9_id', 'away_batter_9_name', 'away_batter_9_pos', 'home_batter_1_id', 'home_batter_1_name', 'home_batter_1_pos', 'home_batter_2_id', 'home_batter_2_name', 'home_batter_2_pos', 'home_batter_3_id', 'home_batter_3_name', 'home_batter_3_pos', 'home_batter_4_id', 'home_batter_4_name', 'home_batter_4_pos', 'home_batter_5_id', 'home_batter_5_name', 'home_batter_5_pos', 'home_batter_6_id', 'home_batter_6_name', 'home_batter_6_pos', 'home_batter_7_id', 'home_batter_7_name', 'home_batter_7_pos', 'home_batter_8_id', 'home_batter_8_name', 'home_batter_8_pos', 'home_batter_9_id', 'home_batter_9_name', 'home_batter_9_pos', 'additional_info', 'acquisition']

    file_name = 'GL%i.TXT' % year
    gl_file = join(dirname(__file__), 'data', 'gamelogs', file_name)
    if isfile(gl_file):
        df = pd.read_csv(gl_file, header = None, names = columns)
        df['game_date'] = df.game_date.astype(str)
        df['game_id'] = df.home_team_id + df.game_date + df.game_number.astype(str)
        df['game_date'] = pd.to_datetime(df.game_date, format = '%Y%m%d')
    else:
        df = pd.DataFrame()
    return df

def get_commands():
    """Creates commands to call chadwick parser"""
    system = platform.system()
    if system == 'Windows':
        event_exe = join(dirname(__file__), 'data', 'exe', 'cwevent.exe')
        sub_exe = join(dirname(__file__), 'data', 'exe', 'cwsub.exe')
    elif system == 'Darwin':
        event_exe = 'cwevent'
        sub_exe = 'cwsub'
    elif system == 'Linux':
        event_exe = None
        sub_exe = None
        raise ValueError('Linux system not supported')
    else:
        raise ValueError('Cannot find system platform')
    return event_exe, sub_exe

def get_retro_event_df(year):
    event_exe, sub_exe = get_commands()

    working_dir = join(dirname(__file__), 'data', 'event', str(year))
    if isdir(working_dir):
        args  = ' -f 0-96 -x 0-60 -n -y %i *.EV*' % year
        cmd = event_exe + args
        output = subprocess.check_output(args = cmd, cwd = working_dir, shell = True)
        df = pd.read_csv(BytesIO(output), low_memory = False)
        column_names = []
        for c in df.columns.values:
            name_lower = c.lower()
            ### normalizedmac and pc output different default column names
            if 'res' in name_lower and 'resp' not in name_lower:
                column_names.append(name_lower.replace('res', 'resp'))
            else:
                column_names.append(name_lower)
        df.columns = column_names
        df['home_team_id'] = df.game_id.str[:3]
        df['game_date'] = pd.to_datetime(df.game_id.str[3:11], format = '%Y%m%d')
    else:
        df = pd.DataFrame()

    return df

def get_retro_subs_df(year):
    system = platform.system()
    event_exe, sub_exe = get_commands()

    working_dir = join(dirname(__file__), 'data', 'event', str(year))
    if isdir(working_dir):
        args = ' -n -y %s *.EV*' % year
        cmd = sub_exe + args
        output = subprocess.check_output(args = cmd, cwd = working_dir, shell = True)
        df = pd.read_csv(BytesIO(output), low_memory = False)
        df.columns = [c.lower() for c in df.columns.values]
    else:
        df = pd.DataFrame()
    return df

def get_team_df():
    team_data = download.download_teams()
    if team_data is not None:
        team_data = BytesIO(team_data)
        columns = ['cur_fran_id', 'fran_id', 'lg', 'div', 'location','name',
                   'alt_name', 'start_date', 'end_date', 'city', 'state']
        df = pd.read_csv(team_data, header = None, names = columns, parse_dates = ['start_date', 'end_date'])
    else:
        df = pd.DataFrame()
    return df

def get_person_df():
    person_data = download.download_people()
    if person_data is not None:
        person_data = BytesIO(person_data)
        df = pd.read_csv(person_data, low_memory = False)
    else:
        df = pd.DataFrame()
    return df

def get_park_df():
    park_data = download.download_parks()
    if park_data is not None:
        park_data = BytesIO(park_data)
        df = pd.read_csv(park_data)
        df.columns  = ['park_id', 'name', 'alias', 'city', 'state', 'country']
        df['venue_id'] = df.park_id.map(constants.PARK_ID)
    else:
        df = pd.DataFrame()
    return df

def decimal_search(search_string):
    regex = r'\d+.\d+'
    temp = re.compile(regex).findall(search_string)
    if len(temp) > 0:
        return temp[0]
    else:
        return None

def get_weather_data():

    venue_data = constants.VENUE_DATA

    session = database.get_session()
    engine = database.get_engine()

    start_date_time = session.query(models.Weather.date_time).order_by\
                            (models.Weather.date_time.desc()).first()

    if start_date_time is not None:
        start_date = start_date_time[0].date() + dt.timedelta(days = 1)
    else:
        start_date = dt.date(2010,1,1)
    start_date = dt.date(2016,1,1)

    delta = dt.date.today() - start_date
    processing_year = start_date.year
    print('Downloading Weather Data for %i.' % processing_year)
    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        if game_date.year != processing_year:
            processing_year = game_date.year
            print('Downloading Weather Data for %i.' % processing_year)

        gids = session.query(models.Game.gid, models.Game.venue_id).filter((models.Game.game_date == game_date) & \
                            models.Game.ind.in_(['F', 'FO', 'FR', 'FG', 'FT'])).all()

        df = pd.DataFrame()
        for row in gids:
            gid = row[0]
            venue = row[1]

            response = download.download_weather_table(gid, venue)

            date_str = gid[:11]
            park_id = venue_data[venue]['park_id']

            data = []
            matches = re.compile(r'<tr class="no-metars">(.*?)<\/tr>').findall(response)
            for match in matches:
                td = re.compile(r'.+?(?=<\/td>)').findall(match)
                time_str = re.search(r'\d{2}:\d{2} [a-zA-Z]{2}', td[0])
                if time_str is None:
                    time_str = re.search(r'\d{1}:\d{2} [a-zA-Z]{2}', td[0]).group()
                else:
                    time_str = time_str.group()
                date_time = dt.datetime.strptime(date_str + time_str, '%Y_%m_%d_%I:%M %p')
                temperature = decimal_search(td[1])
                heat_index = decimal_search(td[2])
                dew_point = decimal_search(td[3])
                humidity =decimal_search(td[4])
                pressure = decimal_search(td[5])
                visibility = decimal_search(td[6])
                wind_dir_text = td[7].split('>')[-1].replace('\\n', '').replace(' ', '').replace('-', '')
                if wind_dir_text in constants.WIND_DIR:
                    wind_dir = constants.WIND_DIR[wind_dir_text]
                else:
                    wind_dir = None
                wind_speed = decimal_search(td[8])
                if wind_speed is None:
                    wind_speed = decimal_search(td[8])
                gust_speed = decimal_search(td[8])
                if gust_speed is None:
                    gust_speed = decimal_search(td[8])
                precip = decimal_search(td[9])

                data.append([gid, venue, park_id, date_time, temperature, heat_index, dew_point, humidity, pressure, visibility, wind_dir, wind_speed, gust_speed, precip])

            columns = ['gid', 'venue_id', 'park_id', 'date_time', 'temperature', 'heat_index', 'dew_point', 'humidity', 'pressure', 'visibility', 'wind_dir', 'wind_speed', 'gust_speed', 'precipitation']

            game_df = pd.DataFrame(data, columns = columns).drop_duplicates(subset = ['gid', 'date_time'])
            df = df.append(game_df)
        if len(df) > 0:
            df.loc[df.heat_index.isnull(), 'heat_index'] = df[df.heat_index.isnull()].temperature
            df.to_sql('weather', engine, if_exists = 'append', index = False)

    session.close()
