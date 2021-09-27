#!/usr/bin/python3
#
# This is a hack to automate results entry in iSquash, but it'll only work on
# Linux because it effectively simulates key strokes. It is assumed that you
# are using [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/),
# and that you enter into score into the game comments in the following
# format: "1-11 11-5 11-6 7-11 6-11" if player B won in 5.
#
# For instance, to enter the results for draw M3 round 3, you run:
#
# % sleep 5 && ./isquash_results_entry.py tc2web/export-fixed.xls M33 | xmacroplay :0
#
# and switch to the browser, where the results entry page better be loaded
# with the cursor in the first field, or here be dragons. I mean it, this tool
# will pretend you are typing, so if you have another window active, it will
# receive the keystrokes.
#
# One idea to make this platform-independent is to use
# [Selenium](https://www.selenium.dev) to lead the browser interaction.
#
# Copyright © 2021 by martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence.
#

import sys
import xlrd
import re

class IncompleteError(BaseException):
    pass

class InconsistentError(BaseException):
    pass

workbook = xlrd.open_workbook(sys.argv[1])
games = workbook.sheet_by_name('Games')

draw = sys.argv[2]
output = []
for row in range(1, games.nrows):
    game = games.row_values(row)
    if not game[0].startswith(draw):
        continue

    scores = []
    if game[10] <= 0:
        sets = game[11].split()
        ac, bc = 0, 0
        for s in sets:
            a, b = map(int, s.split('-'))
            if a > b:
                ac += 1
            elif a < b:
                bc += 1
            else:
                raise IncompleteError
            scores.append((a, b))

        if ac > bc and ( game[3] != 1 or game[6] != 0 ):
                raise InconsistentError(game)
        if bc > ac and ( game[6] != 1 or game[3] != 0 ):
                raise InconsistentError(game)

    print(f'{game[0]}: {scores}', file=sys.stderr)

    if len(scores) < 5:
        scores += [(0,0) for i in range(5-len(scores))]

    output.append(scores)

def insert(string):
    for char in string:
        if char.isalpha():
            print('KeyStrPress Shift_L')
        print(f'KeyStrPress {char}')
        print(f'KeyStrRelease {char}')
        if char.isalpha():
            print('KeyStrRelease Shift_L')

def clear_field():
    print("""KeyStrPress Control_L
KeyStrPress a
KeyStrRelease a
KeyStrRelease Control_L
KeyStrPress Delete
KeyStrRelease Delete""")

def move_next():
    print("KeyStrPress Tab\nKeyStrRelease Tab")

for match in output:
    for game in match:
        clear_field()
        insert(f'{game[0]}')
        move_next()
        clear_field()
        insert(f'{game[1]}')
        move_next()
