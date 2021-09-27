#!/usr/bin/python3
#
# Mail-merges the text in the argument with data from the draw maker.
#
# Usage:
#   ./player_mmerge.py draw_maker.ods "Hello {First name} {Squash Code}"
#
# The available field names are exactly the columns names in the
# Men's/Women's Draws tabs in the draw_maker.ods file.
#
# It would be nice if this tool could somehow include a filter to select e.g.
# only the players matching a certain pattern, such as "on the waiting list"
# or "from this club" or "this region".
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import pyexcel
import argparse

parser = argparse.ArgumentParser(description='Mail merge draw data')

inputg = parser.add_argument_group(title='Input')
inputg.add_argument('draw_maker', metavar='SPREADSHEET', type=str,
        nargs=1, help='Draws spreadsheet to read')
inputg.add_argument('--all', '-a', action="store_true",
        help="Read all players, not just those in draws")

indata = inputg.add_mutually_exclusive_group(required=True)
indata.add_argument('--file', '-f', metavar='TEMPLATE', default=None,
        type=str, nargs=1, help='Template file to use for the merge')
indata.add_argument('text', metavar='TEMPLATE_TEXT', type=str,
        nargs='*', default='', help='Template text to use for merge')

filterg = parser.add_argument_group(title='Filters')
filterg.add_argument('--waitlist', '-w', action="store_true",
        dest='waitlist', help='Limit to players on waitlist (see also --all)')
filterg.add_argument('--gender', '-g', type=str, metavar='GENDER',
        choices=['m','f'], dest='gender', default=None,
        help='Limit to players of the specified gender')
filterg.add_argument('--code', '-c', type=str, metavar='CODE',
        dest='code', help='Limit to players whose codes start with CODE')
filterg.add_argument('--points', '-p', type=str, metavar='FROM-TO',
        default=None,
        help='Limit to players within points range')
filterg.add_argument('--invert', '-i', action="store_true",
        dest='invert', default=False,
        help='Invert the filter criteria')

args = parser.parse_args()

if args.file:
    try:
        with open(args.file[0], "r") as f:
            template = f.read().strip()
    except FileNotFoundError as e:
        print(f'{e.strerror}: {e.filename}', file=sys.stderr)
        sys.exit(1)
else:
    template = " ".join(args.text)

if args.all:
    sheet_name = '{gender}'
    row_offset = 2
    skip_cols = ['male', 'female', 'r', 'w', 'source']

else:
    sheet_name = "{gender}'s Draws"
    row_offset = 8
    skip_cols = ['men', 'women']

workbook = pyexcel.load_book(args.draw_maker[0])
sheets = []

if args.gender != 'f':
    wb = workbook.sheet_by_name(sheet_name.format(gender='Men'))
    sheets.append((wb, 'm'))
if args.gender != 'm':
    wb = workbook.sheet_by_name(sheet_name.format(gender='Women'))
    sheets.append((wb, 'f'))

colnames = sheets[0][0].row_at(row_offset-1)
cols = {}
for i, n in enumerate(colnames):
    try:
        n = n.lower()
    except AttributeError:
        # skip over integer columns
        continue
    if n in skip_cols:
        continue
    cols[n] = i

if args.points:
    p = args.points.split('-')
    points_min = int(p[0])
    points_max = int(p[1]) if len(p) > 1 else points_min

else:
    points_min, points_max = 0, 9999

for draws, gender in sheets:
    count = draws.number_of_rows()
    for player in range(row_offset, count):
        row = draws.row_at(player)
        if not row[0]: continue

        data = {'gender': gender}
        for k,i in cols.items():
            data[k] = row[i]
            # It might would be good to turn week day names into actual dates,
            # as shown below, but obviously not hard-coded into the file.

            #if data[k] == 'Wed':
            #    data[k] = 'Wed 29 Sep'
            #elif data[k] == 'Thu':
            #    data[k] = 'Thu 30 Sep'
            #elif data[k] == 'Fri':
            #    data[k] = 'Fri 1 Oct'
            #elif data[k] == 'Sat':
            #    data[k] = 'Sat 2 Oct in the morning'

        if args.waitlist and data['wl'] == args.invert:
            continue

        elif args.code and data['squash code'].startswith(args.code) == args.invert:
            continue

        elif (data['points'] >= points_min and data['points'] <= points_max) == args.invert:
            continue

        try:
            print(template.format(**data))
        except KeyError as e:
            arg = e.args[0].lower()
            if arg in data:
                print(f"Field {e} should be all lower-case: {arg}",
                        file=sys.stderr)
            else:
                print(f"Field {e} is not one of {', '.join(data.keys())}",
                        file=sys.stderr)
            sys.exit(0)
