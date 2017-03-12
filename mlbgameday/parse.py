"""
This module parses individual game data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
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

def get_players(game):
    """Returns all players for a game dictonary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_players')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'players.xml')
    root = ET.fromstring(data)
    players = []
    for elem in root:
        if elem.tag == 'team':
            if elem.attrib['type'] == 'home':
                home_flag = 1
            else:
                home_flag = 0
            player_nodes = elem.findall('player')
            for person in player_nodes:
                player = {'gid': gid, 'game_pk': game_pk, 'home_flag': home_flag}
                for attr in person.attrib:
                    player[attr] = person.attrib[attr]
                players.append(player)
    return players

def get_coaches(game):
    """Returns all coaches for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_coaches')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'players.xml')
    root = ET.fromstring(data)
    coaches = []
    for elem in root:
        if elem.tag == 'team':
            if elem.attrib['type'] == 'home':
                home_flag = 1
            else:
                home_flag = 0
            coach_nodes = elem.findall('coach')
            for person in coach_nodes:
                coach = {'gid': gid, 'game_pk': game_pk, 'home_flag': home_flag}
                for attr in person.attrib:
                    coach[attr] = person.attrib[attr]
                coaches.append(coach)
    return coaches

def get_umpires(game):
    """Returns all umpires for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_umpires')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'players.xml')
    root = ET.fromstring(data)
    umpires = []
    umpire_nodes = root.find('umpires').findall('umpire')
    for person in umpire_nodes:
        umpire = {'gid': gid, 'game_pk': game_pk}
        for attr in person.attrib:
            umpire[attr] = person.attrib[attr]
        umpires.append(umpire)
    return umpires

def get_hip(game):
    """Returns hip points for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_hip')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'inning_hip.xml')
    root = ET.fromstring(data)
    hips = []
    hip_nodes = root.findall('hip')
    for node in hip_nodes:
        hip = {'gid': gid, 'game_pk': game_pk}
        for attr in node.attrib:
            hip[attr] = node.attrib[attr]
        hips.append(hip)
    return hips

def get_atbats(game):
    """Returns atbats for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_atbats')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    atbats = []
    innings = root.findall('inning')
    halves = {'top': 'top', 'bottom': 'bot'}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            inning_topbot = halves[half]
            inning_node = inning.find(half)
            if inning_node is not None:
                atbat_nodes = inning_node.findall('atbat')
                for node in atbat_nodes:
                    atbat = {'gid': gid, 'game_pk': game_pk, 'inning_topbot': inning_topbot, 'inning': inning_number}
                    for attr in node.attrib:
                        atbat[attr] = node.attrib[attr]
                    atbat = get_child(node, atbat, 'pitch')
                    atbat = get_child(node, atbat, 'runner')
                    atbat = get_child(node, atbat, 'po')
                    atbats.append(atbat)
    return atbats

def get_child(atbat_node, atbat, child_name):
    """Returns atbat dictionary with pitches for xml node and atbat dictionary"""
    gid = atbat['gid']
    game_pk = atbat['game_pk']
    inning_topbot = atbat['inning_topbot']
    inning_number = atbat['inning']
    bat_num = atbat['num']
    child_nodes = atbat_node.findall(child_name)
    children = []
    for child in child_nodes:
        child_dict = {'gid': gid, 'game_pk': game_pk, 'inning_topbot': inning_topbot, 'inning': inning_number, 'bat_num': bat_num}
        for attr in child.attrib:
            child_dict[attr] = child.attrib[attr]
        if 'id' in child_dict:
            child_dict[child_name + '_id'] = child_dict.pop('id','')
        children.append(child_dict)
    atbat[child_name] = children
    return atbat

def get_runners(game):
    """Returns runners for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_runners')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    runners = []
    innings = root.findall('inning')
    halves = {'top': 'top', 'bottom': 'bot'}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            inning_topbot = halves[half]
            inning_node = inning.find(half)
            if inning_node is not None:
                atbat_nodes = inning_node.findall('atbat')
                for bat_node in atbat_nodes:
                    runner_nodes = bat_node.findall('runner')
                    bat_num = bat_node.attrib['num']
                    for node in runner_nodes:
                        runner = {'gid': gid, 'game_pk': game_pk, 'inning_topbot': inning_topbot, 'inning': inning_number, 'bat_num': bat_num}
                        for attr in node.attrib:
                            runner[attr] = node.attrib[attr]
                        runners.append(runner)
    return runners

def get_pickoffs(game):
    """Returns runners for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_pickoffs')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    pickoffs = []
    innings = root.findall('inning')
    halves = {'top': 'top', 'bottom': 'bot'}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            inning_topbot = halves[half]
            atbat_nodes = inning.find(half).findall('atbat')
            for bat_node in atbat_nodes:
                po_nodes = bat_node.findall('po')
                bat_num = bat_node.attrib['num']
                for node in po_nodes:
                    po = {'gid': gid, 'game_pk': game_pk, 'inning_topbot': inning_topbot, 'inning': inning_number, 'bat_num': bat_num}
                    for attr in node.attrib:
                        po[attr] = node.attrib[attr]
                    pickoffs.append(po)
    return pickoffs

def get_actions(game):
    """Returns actions for a game dictionary"""
    if 'gid' in game:
        gid = game['gid']
    else:
        print('No gid for game')
        print(game)
        raise ValueError('gid key required for get_actions')
    if 'game_pk' in game:
        game_pk = game['game_pk']
    else:
        game_pk = ''
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    actions = []
    innings = root.findall('inning')
    halves = {'top': 'top', 'bottom': 'bot'}
    action_number = 1
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            inning_topbot = halves[half]
            inning_node = inning.find(half)
            if inning_node is not None:
                action_nodes = inning_node.findall('action')
                for node in action_nodes:
                    action = {'gid': gid, 'game_pk': game_pk, 'inning_topbot': inning_topbot, 'inning': inning_number, 'action_number': action_number}
                    for attr in node.attrib:
                        action[attr] = node.attrib[attr]
                    actions.append(action)
                    action_number += 1
    return actions

def get_trajectory_df(year):
    files_dir = join(dirname(__file__), 'data/savant', str(year))
    player_files = [f for f in listdir(files_dir) if isfile(join(files_dir, f))]
    df = pd.DataFrame()
    for file_name in player_files:
        file_path = join(files_dir, file_name)
        with gzip.open(file_path, 'rt') as f:
            data = StringIO(f.read())
        df = df.append(pd.read_csv(data, parse_dates = ['game_date', 'tfs_zulu']))
    return df
