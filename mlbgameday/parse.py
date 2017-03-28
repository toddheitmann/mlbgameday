"""
This module parses individual game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

import gzip
from os import listdir
from os.path import isfile, join, dirname
import datetime as dt
import xml.etree.ElementTree as ET
import pandas as pd

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import download as dl

def get_players(gid, game_pk, game_date):
    data = dl.download_gid_file(gid, 'players.xml')
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
                    player = {'gid': gid, 'game_pk': game_pk, 'home_flag': home_flag, 'game_date': game_date}
                    player = dl.get_attributes(player, person, 'player')
                    if len(player['first']) < 1:
                        # mlb errors for player allocation at games example:
                        # http://gd2.mlb.com/components/game/mlb/year_2010/
                        # month_03/day_13/gid_2010_03_13_minmlb_phimlb_1/players.xml
                        continue
                    players.append(player)
            coach_nodes = elem.findall('coach')
            if coach_nodes is not None:
                for person in coach_nodes:
                    coach = {'gid': gid, 'game_pk': game_pk, 'home_flag': home_flag, 'game_date': game_date}
                    coach = dl.get_attributes(coach, person, 'coach')
                    coaches.append(coach)
        elif elem.tag == 'umpires':
            umpire_nodes = elem.findall('umpire')
            if umpire_nodes is not None:
                for person in umpire_nodes:
                    umpire = {'gid': gid, 'game_pk': game_pk, 'game_date': game_date}
                    umpire = dl.get_attributes(umpire, person, 'umpire')
                    umpires.append(umpire)
    return {'players': players, 'coaches': coaches, 'umpires': umpires}

def get_hip(gid, game_pk):
    data = dl.download_gid_file(gid, 'inning_hip.xml')
    root = ET.fromstring(data)
    hips = []
    hip_nodes = root.findall('hip')
    for node in hip_nodes:
        hip = {'gid': gid, 'game_pk': game_pk}
        hip = dl.get_attributes(hip, node, 'hip')
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

def get_events(gid, game_pk, venue_id):
    """Returns event dictionary list for specificed game and venue"""

    ### setup game variables ###
    halves = {'top': 'top', 'bottom': 'bot'}
    bases = {'1B': None, '2B': None, '3B': None, '': None}
    runs = {'home_team_runs': 0, 'away_team_runs': 0}
    players = get_players(gid, game_pk)
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
    data = dl.download_gid_file(gid, 'inning_all.xml')
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
                    event = {'gid': gid, 'game_pk': game_pk, 'venue_id': venue_id, 'inning_topbot': inning_topbot, 'inning': inning_number, 'game_event_number': game_event_number, 'umpire': home_umpire, 'catcher': catcher[inning_topbot] ,'start_outs': outs}
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
                        atbat = dl.get_attributes(atbat, node, 'atbat')
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
                                pitch = dl.get_attributes(pitch, child, 'pitch')
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
                                runner = dl.get_attributes(runner, child, 'runner')

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
                                po = dl.get_attributes(po, child, 'pickoff')

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
                        action = dl.get_attributes(action, node, 'action')
                        base_state = get_base_state(bases)
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

def get_trajectory_df(year):
    """reads downloaded csv files into pandas dataframe"""
    files_dir = join(dirname(__file__), 'data/savant', str(year))
    player_files = [f for f in listdir(files_dir) if isfile(join(files_dir, f))]
    df = pd.DataFrame()
    for file_name in player_files:
        file_path = join(files_dir, file_name)
        with gzip.open(file_path, 'rt') as f:
            data = StringIO(f.read())
        df = df.append(pd.read_csv(data, parse_dates = ['game_date', 'tfs_zulu']))
    return df
