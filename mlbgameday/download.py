"""
This module downloads data from mlbgameday, which is subject to the license at:
http://gd2.mlb.com/components/copyright.txt
"""

import os
import gzip
import datetime as dt
import xml.etree.ElementTree as et

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
        except HTTPError:
            print('HTTPError')
            path = None

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
