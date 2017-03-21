"""
This module is for testing future function with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

import parse as p
import download as dl
import datetime as dt

from models import *
import database as db

from sqlalchemy import and_, or_

def get_events(game_date):
    games = dl.get_games(game_date)
    objects = []
    for game in games:
        events = p.get_events(game['gid'], game['game_pk'], game['venue_id'])
        for event in events:
            if event['event_type'] == 'atbat':
                pickoffs = event.pop('pickoffs', [])
                for pickoff in pickoffs:
                    obj = models.Pickoff(**pickoff)
                    if obj is not None:
                        objects.append(models.Pickoff(**pickoff))
                runners = event.pop('runners', [])
                for runner in runners:
                    obj = models.Runner(**runner)
                    if obj is not None:
                        objects.append(obj)
                pitches = event.pop('pitches', [])
                for pitch in pitches:
                    obj = models.Pitch(**pitch)
                    if obj is not None:
                        objects.append(obj)
                obj = models.Event(**event)
                if obj is not None:
                    objects.append(obj)
            elif event['event_type'] == 'action':
                obj = models.Event(**event)
                if obj is not None:
                    objects.append(obj)
    return objects

query = db.MLBQuery(Game).filter(or_(Game.home_team_runs == None, Game.away_team_runs)).frame()

print(len(query))

# session = db.create_session()
# start_date = dt.date(2010,1,1)
# end_date = dt.date(2017,1,1)
# delta = end_date - start_date
#
# year = 2010
# dates = []
# for d in range(delta.days):
#     dates.append(start_date + dt.timedelta(d))
#
# print(year)
# objects = []
# for d in dates:
#     if d.year != year:
#         year = d.year
#         print(year)
#     games = dl.get_games(d)
#     for game in games:
#         objects.append(models.Game(**game))
# session.bulk_save_objects(objects)
# session.commit()

# actions = p.get_actions(game)

# num_events = 0
# for a in actions:
#     if int(a['event_num']) > num_events:
#         num_events = int(a['event_num'])
#
# for b in atbats:
#     if int(b['event_num']) > num_events:
#         num_events = int(b['event_num'])
#
# for e in range(num_events):
#     for a in actions:
#         if int(a['event_num']) == e:
#             print('Event Number: ' + str(e))
#             print('Action: ' + a['event'] + ' : ' + a['des'])
#             for a in atbats:
#                 for r in a['runner']:
#                     if int(r['event_num']) == e:
#                         print('Runner: ' + r['event'])

# for bat in atbats[3]:
#     print(bat)
