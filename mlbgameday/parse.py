"""
This module parses individual game data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
"""

import os
import datetime as dt
import xml.etree.ElementTree as ET

import download as dl

def get_games(game_date):
    """Returns general game data for a date"""
    data = dl.download_miniscoreboard(game_date)
    root = ET.fromstring(data)
    games = []
    for game in root:
        if game.tag == 'game':
            game_info = {}
            for attr in game.attrib:
                if 'link' not in attr:
                    game_info[attr] = game.attrib[attr]
            games.append(game_info)
    return games

def get_players(gid):
    """Returns all players for a gid"""
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
                player = {'gid': gid, 'home_flag': home_flag}
                for attr in person.attrib:
                    player[attr] = person.attrib[attr]
                players.append(player)
    return players

def get_coaches(gid):
    """Returns all coaches for a gid"""
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
                coach = {'gid': gid, 'home_flag': home_flag}
                for attr in person.attrib:
                    coach[attr] = person.attrib[attr]
                coaches.append(coach)
    return coaches

def get_umpires(gid):
    """Returns all umpires for a gid"""
    data = dl.download_gid_file(gid, 'players.xml')
    root = ET.fromstring(data)
    umpires = []
    umpire_nodes = root.find('umpires').findall('umpire')
    for person in umpire_nodes:
        umpire = {'gid': gid}
        for attr in person.attrib:
            umpire[attr] = person.attrib[attr]
        umpires.append(umpire)
    return umpires

def get_hip(gid):
    """Returns hip points for gid"""
    data = dl.download_gid_file(gid, 'inning_hip.xml')
    root = ET.fromstring(data)
    hips = []
    hip_nodes = root.findall('hip')
    for node in hip_nodes:
        hip = {'gid': gid}
        for attr in node.attrib:
            hip[attr] = node.attrib[attr]
        hips.append(hip)
    return hips

def get_atbats(gid):
    """Returns atbats for gid"""
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    atbats = []
    innings = root.findall('inning')
    halves = {'top': 0, 'bottom': 1}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            home_flag = halves[half]
            atbat_nodes = inning.find(half).findall('atbat')
            for node in atbat_nodes:
                atbat = {'gid': gid, 'home_flag': home_flag, 'inning': inning_number}
                for attr in node.attrib:
                    atbat[attr] = node.attrib[attr]
                atbats.append(atbat)
    return atbats

def get_pitches(gid):
    """Returns pitches for gid"""
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    pitches = []
    innings = root.findall('inning')
    halves = {'top': 0, 'bottom': 1}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            home_flag = halves[half]
            atbat_nodes = inning.find(half).findall('atbat')
            for bat_node in atbat_nodes:
                pitch_nodes = bat_node.findall('pitch')
                bat_num = bat_node.attrib['num']
                for node in pitch_nodes:
                    pitch = {'gid': gid, 'home_flag': home_flag, 'inning': inning_number, 'bat_num': bat_num}
                    for attr in node.attrib:
                        pitch[attr] = node.attrib[attr]
                    pitches.append(pitch)
    return pitches

def get_runners(gid):
    """Returns runners for gid"""
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    runners = []
    innings = root.findall('inning')
    halves = {'top': 0, 'bottom': 1}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            home_flag = halves[half]
            atbat_nodes = inning.find(half).findall('atbat')
            for bat_node in atbat_nodes:
                runner_nodes = bat_node.findall('runner')
                bat_num = bat_node.attrib['num']
                for node in runner_nodes:
                    runner = {'gid': gid, 'home_flag': home_flag, 'inning': inning_number, 'bat_num': bat_num}
                    for attr in node.attrib:
                        runner[attr] = node.attrib[attr]
                    runners.append(runner)
    return runners

def get_pickoffs(gid):
    """Returns runners for gid"""
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    pickoffs = []
    innings = root.findall('inning')
    halves = {'top': 0, 'bottom': 1}
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            home_flag = halves[half]
            atbat_nodes = inning.find(half).findall('atbat')
            for bat_node in atbat_nodes:
                po_nodes = bat_node.findall('po')
                bat_num = bat_node.attrib['num']
                for node in po_nodes:
                    po = {'gid': gid, 'home_flag': home_flag, 'inning': inning_number, 'bat_num': bat_num}
                    for attr in node.attrib:
                        po[attr] = node.attrib[attr]
                    pickoffs.append(po)
    return pickoffs

def get_actions(gid):
    """Returns atbats for gid"""
    data = dl.download_gid_file(gid, 'inning_all.xml')
    root = ET.fromstring(data)
    actions = []
    innings = root.findall('inning')
    halves = {'top': 0, 'bottom': 1}
    action_number = 1
    for inning in innings:
        inning_number = inning.attrib['num']
        for half in halves:
            home_flag = halves[half]
            action_nodes = inning.find(half).findall('action')
            for node in action_nodes:
                action = {'gid': gid, 'home_flag': home_flag, 'inning': inning_number, 'action_number': action_number}
                for attr in node.attrib:
                    action[attr] = node.attrib[attr]
                actions.append(action)
                action_number += 1
    return actions
