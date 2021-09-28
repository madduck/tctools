#!/usr/bin/python3
#
# Mail-merges the text in the argument with data from the draw maker.
#
# Usage:
#   ./player_mmerge.py draw_maker.ods "Hello {first name} {squash code}"
#
# Please see the output of `./player_mmerge.py --help` for information on
# available filters.
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import os
import pyexcel
import argparse
import datetime
import pytz

try:
    import jinja2
    HAVE_JINJA2=True
except ImportError:
    HAVE_JINJA2=False

parser = argparse.ArgumentParser(description='Mail merge draw data')

inputg = parser.add_argument_group(title='Input')
inputg.add_argument('draw_maker', metavar='SPREADSHEET', type=str,
        nargs=1, help='Draws spreadsheet to read')
inputg.add_argument('--all', '-a', action="store_true",
        help="Read all players, not just those in draws")

indata = inputg.add_mutually_exclusive_group(required=True)
indata.add_argument('text', metavar='TEMPLATE_TEXT', type=str,
        nargs='*', default='', help='Template text to use for merge')
indata.add_argument('--file', '-f', metavar='FILE', default=None,
        type=str, nargs=1, help='File to read template text from')
if HAVE_JINJA2:
    indata.add_argument('--template', '-t', metavar='TEMPLATE', default=None,
            type=str, nargs=1, help='Jinja2 template to be used for the merge')

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

args = parser.parse_args(namespace=argparse.Namespace(template=None))

if args.file or args.template:
    f = args.file or args.template
    try:
        with open(f[0], "r") as inp:
            template = inp.read().strip()
    except FileNotFoundError as e:
        print(f'{e.strerror}: {e.filename}', file=sys.stderr)
        sys.exit(1)

elif not args.template:
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
    points_min = 0
    points_max = -1

resultset = []
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

        if not args.invert:
            if args.waitlist and not data['wl']:
                continue
            elif args.code and not data['squash code'].startswith(args.code):
                continue
            elif args.points and \
                    (data['points'] < points_min or
                     data['points'] > points_max):
                continue
        else:
            if args.waitlist and data['wl']:
                continue
            elif args.code and data['squash code'].startswith(args.code):
                continue
            elif args.points and \
                    (data['points'] >= points_min and
                     data['points'] <= points_max):
                continue

        resultset.append(data)



if not args.template:
    try:
        print('\n'.join(template.format(**d) for d in resultset))

    except KeyError as e:
        arg = e.args[0].lower()
        if arg in data:
            print(f"Field {e} should be all lower-case: {arg}",
                    file=sys.stderr)
        else:
            print(f"Field {e} is not one of {', '.join(data.keys())}",
                    file=sys.stderr)
        sys.exit(1)

else:
    wb = workbook.sheet_by_name('Info')
    tournament_name = wb.row_at(3)[2]

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.getcwd()),
        autoescape=jinja2.select_autoescape(['j2']))
    template = env.from_string(template)
    timestamp = datetime.datetime.now(tz=pytz.timezone('Pacific/Auckland')).strftime('%F % T %Z')
    print(template.render(tournament_name=tournament_name,
                          timestamp=timestamp,
                          dataset=resultset))
