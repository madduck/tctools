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

workbook = pyexcel.load_book(sys.argv[1])
men = workbook.sheet_by_name("Men's Draws")
wmn = workbook.sheet_by_name("Women's Draws")

colnames = men.row_at(7)
cols = {}
for i, n in enumerate(colnames):
    cols[n] = i

for draws, gender in ((men,'m'), (wmn,'f')):
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

        print(" ".join(sys.argv[2:]).format(**data))

        # If you need to filter, for now modify like so:
        #
        # if data['WL']:
        #     print(" ".join(sys.argv[2:]).format(**data))
        #
        # or
        #
        # if data['Squash Code'].startswith('WNTH'):
        #    print(" ".join(sys.argv[2:]).format(**data))
