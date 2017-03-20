"""
This module is for testing future function with game data from mlbgameday,
which is subject to the license at: http://gd2.mlb.com/components/copyright.txt
"""

import parse as p
import download as dl
import datetime as dt

game = dl.get_games(dt.date(2010, 6, 17))[1]

events = p.get_events(game['gid'], game['game_pk'], game['venue_id'])

for e in events:
    if e['start_out_base_state'] != e['end_out_base_state']:
        print(e['event'])
        for r in e['runners']:
            print('%s\t%s\t%s' % (str(r['runner_id']),r['start'], r['end']))
            
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
