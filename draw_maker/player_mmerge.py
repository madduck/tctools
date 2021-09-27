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
indata = inputg.add_mutually_exclusive_group(required=True)
indata.add_argument('--file', '-f', metavar='TEMPLATE', default=None,
        type=str, nargs=1, help='Template file to use for the merge')
indata.add_argument('text', metavar='TEMPLATE_TEXT', type=str,
        nargs='*', default='', help='Template text to use for merge')
filterg = parser.add_argument_group(title='Filters')
filterg.add_argument('--waitlist', '-w', action="store_true",
        dest='waitlist', help='Limit to players in draws AND on the waitlist')
filterg.add_argument('--code', '-c', type=str, metavar='CODE',
        dest='code', help='Limit to players whose codes start with CODE')
filterg.add_argument('--gender', '-g', type=str, metavar='GENDER',
        choices=['m','f'], dest='gender', default=None,
        help='Limit to players of the specified gender')
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

workbook = pyexcel.load_book(args.draw_maker[0])

sheets = []
if args.gender != 'f':
    sheets.append((workbook.sheet_by_name("Men's Draws"), 'm'))
if args.gender != 'm':
    sheets.append((workbook.sheet_by_name("Women's Draws"), 'f'))

colnames = sheets[0][0].row_at(7)
cols = {}
for i, n in enumerate(colnames):
    cols[str(n).lower()] = i

for draws, gender in sheets:
    count = draws.number_of_rows()
    for player in range(8, count):
        row = draws.row_at(player)
        if not row[0]: continue

        data = {'Gender': gender}
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
