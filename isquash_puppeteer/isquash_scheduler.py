#!/usr/bin/python3
#
# This is a hack to automate entering games into time slots on iSquash, should
# you even bother, using data exported from
# [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/).
# It currently only works on Linux Linux because it effectively simulates key
# strokes.
#
# For instance, to enter the the scheduled games for Saturday between 12:00
# and 24:00 assuming there are 4 courts:
#
# % sleep 5 && ./isquash_scheduler.py tc-export-fixed.xls Sat 4 12 24 | xmacroplay :0
#
# and switch to the browser, where the calendar page better be loaded to the
# right day, and with the cursor in the first field, or here be dragons. I
# mean it, this tool will pretend you are typing, so if you have another
# window active, it will receive the keystrokes.
#
# One idea to make this platform-independent is to use
# [Selenium](https://www.selenium.dev) to lead the browser interaction.
#
# Copyright © 2021 by martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence.
#

import sys
import xlrd

workbook = xlrd.open_workbook(sys.argv[1])
games = workbook.sheet_by_name('Games')

def stupid_to_real_time(time):
    ampm = time[-2:]
    hour, minute = time[:-2].split(':')
    hour = int(hour)
    if ampm == 'pm' and hour != 12:
        hour += 12
    return f'{hour}:{minute}'

def real_to_stupid_time(time):
    hour, minute = map(int, time.split(':'))
    ampm = 'am'
    if hour > 12:
        hour -= 12
        ampm = 'pm'
    return f'{hour}:{minute:02d}{ampm}'

hours = {}

for row in range(1, games.nrows):
    day, time = games.cell_value(row, 7).split()
    if day != sys.argv[2]: continue
    code = games.cell_value(row, 0)
    time = stupid_to_real_time(time)
    hour, minute = time.split(':')
    hour = int(hour)
    if hour not in hours:
        hours[hour] = {}
    minute = int(minute)
    if minute not in hours[hour]:
        hours[hour][minute] = []
    hours[hour][minute].append((minute, code))

courts = int(sys.argv[3])

if courts > 7:
    print(f"I don't think you have {courts} courts.", file=sys.stderr)
    sys.exit(1)

begin, end = 0, 24
if len(sys.argv) == 6:
    begin = int(sys.argv[4])
    end = int(sys.argv[5])

import pprint
output = []
for hour in sorted(hours.keys()):
    if hour < begin or hour >= end: continue
    games = []
    for slot in sorted(hours[hour].keys()):
        slotgames = hours[hour][slot]
        while len(slotgames) < courts:
            slotgames.append((slot, ''))

        #if courts == 7:
        #    #TODO hack to schedule island bay games
        #    slotgames.sort(key=lambda x: (0,x) if x[1][0:2] in ('M4', 'M6', 'M8', 'W4') else (1,x))

        games.extend(slotgames)

    count = len(games)
    ngames = [list(range(count)[o::courts]) for o in range(courts)]
    for i in itertools.chain(*ngames):
        game = games[i]
        time = real_to_stupid_time(f'{hour:02d}:{game[0]}')
        print(f'{time} {game[1]}', file=sys.stderr)
        output.append(game[1])

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

for field in output:
    clear_field()
    if field:
        insert(field)
    move_next()
