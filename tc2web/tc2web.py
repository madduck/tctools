#!/usr/bin/python3
#
# Extract games schedule and draws from a TournamentControl
# export spreadsheet, and turn them into a simple HTML view
#
# Expects the score to be entered for finished games in the
# form of 4-11 11-3 11-2 11-6 where the first number always
# refers to the player named first, and the second to the
# player named second.
#
# Copyright © 2021 martin f. krafft <m@rtin.kiwi>
# Released under the MIT Licence
#

import sys
import xlrd
import datetime
import os
import re
import jinja2
import pytz

workbook = xlrd.open_workbook(sys.argv[1])
tournament_name = workbook.sheet_by_name('Tournament').cell_value(rowx=0, colx=1)

###############################################################################
# First get the draws

class Draw:
    def __init__(self, row):
        self.code, self.name = row[0:2]
        # delphi colours are reversed
        self.colour = f'{row[2][7:]}{row[2][5:7]}{row[2][3:5]}'
        self.games = []

    def __repr__(self):
        return self.code

    def __eq__(self, other):
        return self.code.__eq__(other.code)

    def __hash__(self):
        return self.code.__hash__()

    def __lt__(self, other):

        # sort the draws and put women first, because we can
        def women_first(code):
            return code.replace('W', '1').replace('M', '2')
        return women_first(self.code).__lt__(women_first(other.code))

    def append_game(self, game):
        self.games.append(game)

drawrows = workbook.sheet_by_name('Draws')
draws = {}
for rowx in range(1, drawrows.nrows):
    d = Draw(drawrows.row_values(rowx=rowx))
    draws[d.code] = d

###############################################################################
# Let's also collect data about all players, indexed by name

class Player:
    def __init__(self, row):
        self.id, self.name, self.gender, self.code, \
                self.points, self.grade, self.club = row[0:7]

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name.__eq__(other.name)

    def __lt__(self, other):
        return self.name.__lt__(other.name)

    def __repr__(self):
        return self.name

playerrows = workbook.sheet_by_name('Players')
players = {}
for rowx in range(1, playerrows.nrows):
    p = Player(playerrows.row_values(rowx=rowx))
    players[p.name] = p

###############################################################################
# Then the games

class Game:
    def __init__(self, row):
        """Initialise a Game structure from a row in the Excel sheet"""
        self.nr = None
        self.code = row[0]
        self.colour = "#FFFFFF" # default to white

        def replace_winner_loser(s):
            if s[0:2] == 'W ':
                return f'Winner of {s[2:]}'
            elif s[0:2] == 'L ':
                return f'Loser of {s[2:]}'
            else:
                return s

        # Parse the TournamentControl export format. We don't do much
        # sanity checking here because we trust that the file has not
        # been fiddled with, and so the export is consistent…
        self.winner = None
        self.p1classes = []
        self.p1data = None
        if row[1]:
            self.p1 = row[1]
            self.p1data = players[self.p1]
            if int(row[3]) == 1:
                self.p1classes.append('winner')
                self.winner = self.p1
        else:
            self.p1 = replace_winner_loser(row[2])
            self.p1classes.append('unknown')

        self.p2classes = []
        self.p2data = None
        if row[4]:
            self.p2 = row[4]
            self.p2data = players[self.p2]
            if int(row[6]) == 1:
                self.p2classes.append('winner')
                self.winner = self.p2
        else:
            self.p2 = replace_winner_loser(row[5])
            self.p2classes.append('unknown')

        daytime = row[7]
        self.venue = row[8]
        self.court = row[9]
        self.comment = row[11]

        self.statusclasses = []
        if row[10] <= 0:
            if not self.winner:
                self.status = 'Awaiting result'
            else:
                self.status = f'Won by {self.winner} in {len(row[11].split())}'
        elif row[10] == 1:
            self.status = f'On {self.court}'
            self.statusclasses.append('on')
        elif row[10] == 2 and self.court:
            self.status = f'Next on {self.court}'
            self.statusclasses.append('next')
        elif row[10] == 99:
            self.status = ''
            self.statusclasses.append('scheduled')
        else:
            self.status = 'Soon'
            self.statusclasses.append('soon')

        self.day = daytime.split()[0]
        self.time = Game.time_parser(daytime.split()[1])

    def time_parser(timestr):
        """Convert silly 12h time to 24h time"""
        ampm = timestr[-2:]
        hour, minute = timestr[:-2].split(':')
        hour = int(hour)
        if ampm == 'pm' and hour != 12:
            hour += 12
        return datetime.time(hour, int(minute))

    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    def __lt__(self, other):
        if self.day == other.day:
            if self.time == other.time:
                # This ensures that "Loser" games sort before "Winner" games
                # and also otherwise it should not make a difference that
                # games at the same time are sorted by player 1's name
                return self.p1.__lt__(other.p1)
            else:
                return self.time.__lt__(other.time)
        else:
            return Game.WEEKDAYS.index(self.day).__lt__(Game.WEEKDAYS.index(other.day))

    def __repr__(self):
        return f'Game({self.nr} {self.code}, {self.day}, ' \
               f'{self.time.strftime("%H:%M")}, ' \
               f'{self.p1}, {self.p2}, {self.status})'

    def is_played(self):
        return self.winner

    NAMES = { '301' : 'Final',
              '302' : 'Sp.Plate',
              '303' : 'Plate',
              '304' : 'Co.Plate' }
    def get_name(self):
        if self.code[2:] in Game.NAMES:
            return f'{self.code[:2]} {Game.NAMES[self.code[2:]]}'
        else:
            return self.code
    name = property(get_name)

gamerows = workbook.sheet_by_name('Games')
played_games, pending_games = [], []
games = [Game(gamerows.row_values(rowx)) for rowx in range(1, gamerows.nrows)]
games.sort()

# And split them into played and pending, adding the colour attribute
# as we go, and also assign them to draws
for i, game in enumerate(games):
    game.nr = i+1
    for code, draw in draws.items():
        if game.code.startswith(draw.code):
            game.colour = draw.colour
            draw.append_game(game)
    if game.is_played():
        played_games.append(game)
    else:
        pending_games.append(game)

# And finally write out the HTML files. There's a bit of logic in
# the templates still…
timestamp = datetime.datetime.now(tz=pytz.timezone('Pacific/Auckland')).strftime('%F %T %Z')
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()),
    autoescape=jinja2.select_autoescape(['j2'])
)
template = env.get_template('live.j2')
with open('live.html', 'w') as f:
    print(template.render(tournament_name=tournament_name,
        timestamp=timestamp,
        draws=draws,
        players=players,
        pending_games=sorted(pending_games),
        played_games=sorted(played_games),
    ), file=f)
