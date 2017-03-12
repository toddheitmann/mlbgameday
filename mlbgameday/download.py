"""
This module downloads data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
"""

import os
from os.path import isfile, dirname, join, exists
import gzip
import re
import time
import datetime as dt
import xml.etree.ElementTree as ET

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, HTTPError

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
            # if not exists(dir_name):
            #     os.makedirs(dir_name)
            # with gzip.open(file_name + '.gz', 'wb') as f:
            #     f.write('<games></games>'.encode())
            error_file = join(dirname(__file__), 'data/download_errors.txt')
            with open(error_file, 'a+') as f:
                f.write(url + '\n')
            print('HTTPError')
            print(url)
            data = None

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

def get_games(game_date):
    """Returns general game data for a date"""
    pop = ['venue', 'time', 'time_date_aw_lg', 'time_date_hm_lg', 'time_zone', 'away_time', 'away_time_zone', 'away_ampm', 'home_ampm', 'time_zone_aw_lg', 'time_zone_hm_lg', 'time_aw_lg', 'aw_lg_ampm', 'tz_aw_lg_gen', 'time_hm_lg', 'hm_lg_ampm', 'tz_hm_lg_gen', 'scheduled_innings', 'venue_w_chan_loc', 'game_data_directory', 'top_inning', 'tv_station', 'ampm', 'tiebreaker_sw']

    data = download_miniscoreboard(game_date)
    root = ET.fromstring(data)
    games = []
    for game in root:
        if game.tag == 'game':
            game_info = {}
            for attr in game.attrib:
                if 'link' not in attr:
                    game_info[attr] = game.attrib[attr]
            game_info['gid'] = game_info.pop('id','').replace('/','_').replace('-','_')
            games.append(game_info)
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
        print(game_date)
        download_miniscoreboard(game_date)
        time.sleep(1)

def update_gid_files(start_date = None, end_date = None):
    """Updates all gid XML files from start_date to yesterday"""
    if start_date is None:
        start_date = dt.date(2014,6,22)
    if end_date is None:
        end_date = dt.date.today()
    delta = end_date - start_date

    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        print(game_date)
        games = get_games(game_date)
        for game in games:
            if game['status'] == 'Final' or game['status'] == 'Completed Early':
                gid = game['gid']
                download_gid_file(gid, 'players.xml')
                download_gid_file(gid, 'inning_hit.xml')
                download_gid_file(gid, 'inning_all.xml')

def download_trajectory_csvs(start_year = None, end_year = None, overwrite = False):
    """Downloads Baseball Savant CSV Files"""
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
    for player_year in players_years:
        player_year = player_year.split('_')
        player_id = player_year[0]
        year = player_year[1]
        dir_name = join(dirname(__file__), 'data/savant', year)
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

def update_all(start_date = None, end_date = None):
    update_miniscoreboard(start_date = start_date, end_date = end_date)
    update_gid_files(start_date = start_date, end_date = end_date)
    if start_date is not None:
        start_year = start_date.year
    else:
        start_year = None
    if end_date is not None:
        end_year = end_date.year
    else:
        end_date = None
    download_savant_csvs(start_year = start_year, end_year = end_year, overwrite = True)
