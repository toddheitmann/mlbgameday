"""
This module downloads data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
"""

import os
import gzip
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
        dir_name = os.path.join(os.path.dirname(__file__), folder)
        file_path = os.path.join(dir_name, file_name)

        url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/%s' % (year, month, day, file_name)
    else:
        folder = 'data/year_%s/month_%s/day_%s/%s' % (year, month, day, gid)
        dir_name = os.path.join(os.path.dirname(__file__), folder)
        file_path = os.path.join(dir_name, file_name)
        if 'inning' in file_name:
            url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/gid_%s/inning/%s' % (year, month, day, gid, file_name)
        else:
            url = 'http://gd2.mlb.com/components/game/mlb/year_%s/month_%s/day_%s/gid_%s/%s' % (year, month, day, gid, file_name)

    return dir_name, file_path, url

def download_xml(dir_name, file_name, url):
    """Serves xml files located in the dir_path at file_path or downloads from url"""
    if os.path.isfile(file_name + '.gz'):
         with gzip.open(file_name + '.gz', 'rb') as f:
             data = f.read()
    else:
        try:
            call = urlopen(url)
            response = call.read()
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with gzip.open(file_name + '.gz', 'wb') as f:
                f.write(response)
            data = response.decode('utf-8')
            time.sleep(1)
        except HTTPError:
            # if not os.path.exists(dir_name):
            #     os.makedirs(dir_name)
            # with gzip.open(file_name + '.gz', 'wb') as f:
            #     f.write(bytearray('<games></games>', 'utf-8'))
            error_file = os.path.join(os.path.dirname(__file__), 'data/download_errors.txt')
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

def get_gids(game_date):
    """Returns all gid for a date"""
    data = download_miniscoreboard(game_date)
    root = ET.fromstring(data)
    gids = []
    for game in root:
        if game.tag == 'game':
            if 'id' in game.attrib:
                gid = game.attrib['id']
                gid = gid.replace('/','_').replace('-','_')
                gids.append(gid)
    return gids

def update_miniscoreboard(start_date = None, end_date = None):
    """Updates all miniscoreboard XML files from start_date to yesterday"""
    if start_date is None:
        start_date = dt.date(2009,2,25)
    if end_date is None:
        end_date = dt.date.today()
    delta = end_date - start_date

    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        print(game_date)
        download_miniscoreboard(game_date)

def update_gid_files(start_date = None, end_date = None):
    """Updates all gid XML files from start_date to yesterday"""
    if start_date is None:
        start_date = dt.date(2009,2,25)
    if end_date is None:
        end_date = dt.date.today()
    delta = end_date - start_date

    for d in range(delta.days):
        game_date = start_date + dt.timedelta(d)
        print(game_date)
        gids = get_gids(game_date)
        for gid in gids:
            download_gid_file(gid, 'players.xml')
            download_gid_file(gid, 'inning_hit.xml')
            download_gid_file(gid, 'inning_all.xml')

def update_all(start_date = None, end_date = None):
    update_miniscoreboard(start_date = start_date, end_date = end_date)
    update_gid_files(start_date = start_date, end_date = end_date)
