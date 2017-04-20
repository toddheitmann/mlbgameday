"""
This module downloads data from mlbgameday
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

import os
from os.path import isfile, isdir, dirname, join, exists
import shutil
import gzip
import re
import time
import datetime as dt
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from io import BytesIO

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError

import constants

def format_gid_date(gid):
    """Returns date object for gid"""
    year = gid[:4]
    month = gid[5:7]
    day = gid[8:10]
    game_date = dt.date(int(year), int(month), int(day))
    return game_date

def format_download_file(game_date, file_name, gid = None):
    """Formats directory and file path for game date"""
    year = game_date.strftime('%Y')
    month = game_date.strftime('%m')
    day = game_date.strftime('%d')

    if gid is None:
        folder = 'data/year_%s/month_%s/day_%s' % (year, month, day)
        dir_name = join(dirname(__file__), folder)
        file_path = join(dir_name, file_name)

        url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/%s' % (year, month, day, file_name)
    else:
        folder = 'data/year_%s/month_%s/day_%s/%s' % (year, month, day, gid)
        dir_name = join(dirname(__file__), folder)
        file_path = join(dir_name, file_name)
        if 'inning' in file_name:
            url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/gid_%s/inning/%s' % (year, month, day, gid, file_name)
        else:
            url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/gid_%s/%s' % (year, month, day, gid, file_name)

    return dir_name, file_path, url

def download_xml(dir_name, file_name, url):
    """Serves xml files located in the dir_path at file_path or downloads from url"""
    if isfile(file_name + '.gz'):
        with gzip.open(file_name + '.gz', 'rb') as f:
            data = f.read()
    else:
        try:
            call = urlopen(url)
            response = call.read()
            if not exists(dir_name):
                os.makedirs(dir_name)
            with gzip.open(file_name + '.gz', 'wb') as f:
                f.write(response)
            data = response.decode('utf-8')
            time.sleep(1)
        except HTTPError:
            data = '<games></games>'
            if not exists(dir_name):
                os.makedirs(dir_name)
            with gzip.open(file_name + '.gz', 'wb') as f:
                f.write(data.encode())
    return data

def download_miniscoreboard(game_date):
    """Downloads scoreboard xml data for gid"""
    dir_name, file_name, url = format_download_file(game_date, 'miniscoreboard.xml')
    data = download_xml(dir_name, file_name, url)
    return data

def download_gid_file(gid, file_name):
    """Downloads xml file for gid"""
    game_date = format_gid_date(gid)
    dir_name, file_name, url = format_download_file(game_date, file_name, gid = gid)
    data = download_xml(dir_name, file_name, url)
    return data

def download_team_names():
    """Downloads team names from retrosheet.org"""
    url = 'http://www.retrosheet.org/CurrentNames.csv'
    call = urlopen(url)
    response = call.read().decode('utf-8')
    with open('data/CurrentNames.csv','w') as f:
        f.write(response)

def get_attributes(dictionary, xml_node, name):
    """Adds attributes from xml node to a dictionary"""
    attr_float = [
    # game attributes
    'home_games_back', 'away_games_back',
    'home_games_back_wildcard', 'away_games_back_wildcard',
    # player attributes
    'avg', 'era',
    # pitch attributes
    'x', 'y', 'start_speed', 'end_speed', 'sz_top', 'sz_bot', 'pfx_x', 'pfx_z',
    'px', 'pz', 'x0', 'y0', 'z0', 'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az',
    'break_y', 'break_angle', 'break_length', 'type_confidence']

    attr_int = [
    # Game Attributes
    'venue_id', 'home_team_id', 'home_league_id', 'away_team_id', 'away_league_id',
    'home_win', 'home_loss', 'away_win', 'away_loss', 'home_team_runs',
    'away_team_runs', 'home_team_hits', 'away_team_hits', 'home_team_errors',
    'away_team_errors', 'home_team_hr', 'away_team_hr', 'home_team_sb', 'away_team_sb',
    'home_team_so', 'away_team_so', 'series_num', 'ser_home_nbr', 'ser_games', 'scheduled_innings',
    # player attributes
    'id', 'game_pk', 'num', 'team_id', 'parent_team_id', 'hr', 'rbi', 'wins', 'losses',
    'event_num', 'home_team_runs', 'away_team_runs', 'o']

    for attr in xml_node.attrib:
        if attr == 'sv_id':
            if len(xml_node.attrib[attr]) > 0:
                dictionary['sv_id'] = dt.datetime.strptime(xml_node.attrib[attr], '%y%m%d_%H%M%S')
            else:
                dictionary['sv_id'] = None
        elif attr in attr_float:
            try:
                dictionary[attr] = float(xml_node.attrib[attr])
            except:
                dictionary[attr] = None
        elif attr in attr_int:
            if attr == 'rbi' and name == 'runner':
                dictionary[attr] = xml_node.attrib[attr]
            elif ' ' not in xml_node.attrib[attr] and \
                 '-' not in xml_node.attrib[attr] and \
                 'null' not in xml_node.attrib[attr] and \
                 len(xml_node.attrib[attr]) > 0:
                dictionary[attr] = int(xml_node.attrib[attr])
            else:
                dictionary[attr] = None
        else:
            dictionary[attr] = xml_node.attrib[attr]
    if 'id' in dictionary:
        dictionary[name + '_id'] = dictionary.pop('id', None)
    if name == 'pitch':
        if 'type' in dictionary:
            dictionary['p_type'] = dictionary.pop('type', None)
    else:
        if 'type' in dictionary:
            dictionary[name + '_type'] = dictionary.pop('type', None)
    return dictionary

def get_games(game_date):
    """Returns general game data for a date"""
    pop_list = ['id', 'game_id', 'time', 'time_date', 'time_date_aw_lg', 'time_date_hm_lg', 'time_zone', 'ampm', 'time_zone_aw_lg', 'time_zone_hm_lg', 'time_aw_lg', 'aw_lg_ampm', 'tz_aw_lg_gen', 'time_hm_lg', 'hm_lg_ampm', 'tz_hm_lg_gen', 'venue_w_chan_loc', 'time_zone_hm_lg', 'top_inning', 'inning', 'outs', 'mlbtv_link', 'wrapup_link', 'home_audio_link', 'away_audio_link', 'home_preview_link', 'away_preview_link', 'preview_link', 'postseason_tv_link', 'game_data_directory', 'resume_time_date_aw_lg', 'resume_time_date_hm_lg', 'resume_time', 'resume_away_ampm', 'runner_on_base_status']

    data = download_miniscoreboard(game_date)
    root = ET.fromstring(data)
    games = []
    for game_node in root:
        if game_node.tag == 'game':
            game = {}
            game = get_attributes(game, game_node, 'game')
            game['gid'] = game.pop('gameday_link', None)
            game['game_date'] = game_date
            date_string = game_date.strftime('%Y%m%d')
            if len(game['home_time']) == 4:
                # errors with makeup games showing AM for PM games
                # len(3:33) == 4 implies game is in PM
                local_time_str = date_string + game['home_time'] + 'PM'
            else:
                local_time_str = date_string + game['home_time'] + game['home_ampm']
            game['datetime_local'] = dt.datetime.strptime(local_time_str, '%Y%m%d%I:%M%p')
            if ':' in game['time']:
                et_time_str = date_string + game['time'] + game['ampm']
                game['datetime_et'] = dt.datetime.strptime(et_time_str, '%Y%m%d%I:%M%p')
            else:
                game['datetime_et'] = None
            for p in pop_list:
                game.pop(p, None)
            if 'original_date' in game:
                game['original_date'] = dt.datetime.strptime(game['original_date'], '%Y/%m/%d').date()
            if 'resume_time_date' in game:
                game['resume_time_date'] = dt.datetime.strptime(game['resume_time_date'], '%Y/%m/%d %H:%M')
            if 'resume_date' in game:
                game['resume_date'] = dt.datetime.strptime(game['resume_date'], '%Y/%m/%d').date()
            if 'home_code' in game:
                game['home_code'] = game['home_code'].upper()
            if 'away_code' in game:
                game['away_code'] = game['away_code'].upper()
            if game_date == dt.datetime.strptime(game['gid'][:10], '%Y_%m_%d').date():
                game_number = str(int(game['gid'][-1]) - 1)
                game['retro_gid'] = game['home_code'] + game_date.strftime('%Y%m%d') + game_number
                game['year'] = game['datetime_local'].year
                game['month'] = game['datetime_local'].month
                game['day'] = game['datetime_local'].day
                games.append(game)
    return games

def update_miniscoreboard(start_date = None, end_date = None):
    """Updates all miniscoreboard XML files from start_date to yesterday"""
    if start_date is None:
        start_date = dt.date(2010,1,1)
    if end_date is None:
        end_date = dt.date.today()
    delta = end_date - start_date

    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        download_miniscoreboard(game_date)

def update_gid_files(start_date = None, end_date = None):
    """Updates all gid XML files from start_date to yesterday"""
    if start_date is None:
        start_date = dt.date(2010,1,1)
    if end_date is None:
        end_date = dt.date.today()
    delta = end_date - start_date

    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        games = get_games(game_date)
        for game in games:
            if game['status'] == 'Final' or game['status'] == 'Completed Early':
                gid = game['gid']
                download_gid_file(gid, 'players.xml')
                download_gid_file(gid, 'inning_hit.xml')
                download_gid_file(gid, 'inning_all.xml')

def update_xml(start_date = None, end_date = None):
    update_miniscoreboard(start_date = start_date, end_date = end_date)
    update_gid_files(start_date = start_date, end_date = end_date)

def remove_mlbam_downloads():
    start_year = 2010
    end_year = dt.date.today().year
    for year in range(start_year, end_year + 1):
        directory = join(dirname(__file__), 'data', 'year_' + str(year))
        if isdir(directory):
            shutil.rmtree(directory)

def download_trajectory_csvs(start_year = None, end_year = None, overwrite = False):
    """Downloads Baseball trajectory CSV Files"""
    if start_year is None:
        start_year = 2015

    if end_year is None:
        end_year = dt.date.today().year

    pitcher_year_url = 'https://baseballsavant.mlb.com/statcast_search?hfPT=&hfZ=&hfGT=%s&hfPR=&hfAB=&stadium=&hfBBT=&hfBBL=&hfC=&season=%i&player_type=pitcher&hfOuts=&pitcher_throws=&batter_stands=&start_speed_gt=&start_speed_lt=&perceived_speed_gt=&perceived_speed_lt=&spin_rate_gt=&spin_rate_lt=&exit_velocity_gt=&exit_velocity_lt=&launch_angle_gt=&launch_angle_lt=&distance_gt=1&distance_lt=&batted_ball_angle_gt=&batted_ball_angle_lt=&game_date_gt=&game_date_lt=&team=&position=&hfRO=&home_road=&hfInn=&min_pitches=0&min_results=0&group_by=name-year&sort_col=pitches&player_event_sort=start_speed&sort_order=desc&min_abs=0&xba_gt=&xba_lt=&px1=&px2=&pz1=&pz2=&ss_gt=&ss_lt=&is_barrel=#results'

    pitcher_url = 'https://baseballsavant.mlb.com/statcast_search/csv?hfPT=&hfZ=&hfGT=%shfPR=&hfAB=&stadium=&hfBBT=&hfBBL=&hfC=&season=%s&player_type=pitcher&hfOuts=&pitcher_throws=&batter_stands=&start_speed_gt=&start_speed_lt=&perceived_speed_gt=&perceived_speed_lt=&spin_rate_gt=&spin_rate_lt=&exit_velocity_gt=&exit_velocity_lt=&launch_angle_gt=-79&launch_angle_lt=&distance_gt=&distance_lt=&batted_ball_angle_gt=&batted_ball_angle_lt=&game_date_gt=&game_date_lt=&team=&position=&hfRO=&home_road=&hfInn=&min_pitches=0&min_results=0&group_by=name-year&sort_col=pitches&player_event_sort=start_speed&sort_order=desc&min_abs=0&xba_gt=&xba_lt=&px1=&px2=&pz1=&pz2=&ss_gt=&ss_lt=&is_barrel=&type=details&player_id=%s&ep_game_year=%s'

    base_query = 'R%7CPO%7CS%7C'

    players_years = []
    for year in range(start_year, end_year + 1):
        year_url = pitcher_year_url % (base_query, year)
        call = urlopen(year_url)
        response = call.read().decode('utf-8')

        matches = re.compile(r'\d{6}_\d{4}').findall(response)
        matches = list(set(matches))
        players_years += matches
        print('%i Found: %i Matches' % (year, len(matches)))
        time.sleep(1)

    data = []
    download_year = str(start_year)
    print('Downloading Trajectory data for %s.' % download_year)
    for player_year in players_years:
        player_year = player_year.split('_')
        player_id = player_year[0]
        year = player_year[1]
        if year != download_year:
            download_year = year
            print('Downloading Trajectory data for %s.' % download_year)
        dir_name = join(dirname(__file__), 'data', 'trajectory', year)
        file_name = join(dir_name, player_id + '.csv.gz')
        if isfile(file_name) and not overwrite:
             with gzip.open(file_name, 'rb') as f:
                 data.append(f.read())
        else:
            try:
                data_url = pitcher_url % (base_query, year, player_id, year)
                call = urlopen(data_url)
                response = call.read().decode('utf-8')
                response = response.replace('null','').replace('  ','')
                if not exists(dir_name):
                    os.makedirs(dir_name)
                with gzip.open(file_name, 'wb') as f:
                    f.write(response.encode())
                data.append(response)
                time.sleep(1)
            except HTTPError:
                if not exists(dir_name):
                    os.makedirs(dir_name)
                with gzip.open(file_name + '.gz', 'wb') as f:
                    f.write(''.encode())

def remove_trajectory_downloads():

    directory = join(dirname(__file__), 'data', 'trajectory')
    if isdir(directory):
        shutil.rmtree(directory)

def download_retrosheet(start_year = None, end_year = None):
    """Downloads retrosheet game logs and event files"""

    if start_year is None:
        start_year = 1871
    if end_year is None:
        end_year = dt.date.today().year

    raw_dir = join(dirname(__file__), 'data')
    for i in range(start_year, end_year):
        ### download gamee files ###
        url_format = "http://www.retrosheet.org/gamelogs/gl%i.zip" % i
        try:
            url = urlopen(url_format)
            zipfile = ZipFile(BytesIO(url.read()))
            save_dir = join(raw_dir, 'gamelogs')
            if not isdir(save_dir):
                os.makedirs(save_dir)
            zipfile.extractall(save_dir)
        except:
            ### year does not contain gamelog files ###
            do = 'nothing'

        ## download event files after 1920 ###
        if i > 1920:
            url_format = "http://www.retrosheet.org/events/%ieve.zip" % i
            try:
                url = urlopen(url_format)
                zipfile = ZipFile(BytesIO(url.read()))
                save_dir = join(raw_dir, 'event', str(i))
                if not isdir(save_dir):
                    os.makedirs(save_dir)
                zipfile.extractall(save_dir)
            except:
                ### year does not contain event files ###
                do = 'nothing'

def get_url_data(url):
    try:
        call = urlopen(url)
        response = call.read()
    except:
        ### 404 error ###
        response = None
    return response

def download_teams():
    url = 'http://www.retrosheet.org/CurrentNames.csv'
    return get_url_data(url)

def download_people():
    url = 'https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv'
    return get_url_data(url)

def download_parks():
    url = 'https://raw.githubusercontent.com/chadwickbureau/baseballdatabank/master/core/Parks.csv'
    return get_url_data(url)

def remove_retrosheet_downloads():

    directory = join(dirname(__file__), 'data', 'gamelogs')
    if isdir(directory):
        shutil.rmtree(directory)

    directory = join(dirname(__file__), 'data', 'event')
    if isdir(directory):
        shutil.rmtree(directory)

def download_weather_table(gid, venue):
    venue_data = constants.VENUE_DATA

    year = gid[:4]
    month = gid[5:7]
    day = gid[8:10]
    zip_code = venue_data[venue]['zip']
    airport = venue_data[venue]['airport']

    base_url = 'https://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?reqdb.zip=%s'
    url_format = base_url % (airport, year, month, day, zip_code)
    url = urlopen(url_format)
    response = repr(url.read())
    time.sleep(1)
    return response
