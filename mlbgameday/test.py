import parse as p
import download as dl
import datetime as dt

game = dl.get_games(dt.date(2010, 6, 17))[1]

atbats = p.get_atbats(game)

actions = p.get_actions(game)

num_events = 0
for a in actions:
    if int(a['event_num']) > num_events:
        num_events = int(a['event_num'])

for b in atbats:
    if int(b['event_num']) > num_events:
        num_events = int(b['event_num'])

for e in range(num_events):
    for a in actions:
        if int(a['event_num']) == e:
            print('Event Number: ' + str(e))
            print('Action: ' + a['event'] + ' : ' + a['des'])
            for a in atbats:
                for r in a['runner']:
                    if int(r['event_num']) == e:
                        print('Runner: ' + r['event'])

# for bat in atbats[3]:
#     print(bat)
