#!/usr/bin/python3
#
# Exports all registered players including waiting list to a
# simple TSV format suitable for Mailchimp import. The second
# argument is the tag base, and '-wl' will be appended for
# players on the waiting list.
#
# Usage:
#   ./mail_list_export.py draw_maker.ods 2021-10-open | xclip -i
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import pyexcel

workbook = pyexcel.load_book(sys.argv[1])
men = workbook.sheet_by_name("Men")
wmn = workbook.sheet_by_name("Women")

COLUMNS = ['Name', 'First name', 'Email', 'WL']

colnames = men.row_at(1)
cols = {}
for i, n in enumerate(colnames):
    if n in COLUMNS and n not in cols:
        # only store the first column if there are duplicates, such as
        # "Name"
        cols[n] = i

COLUMNS[3] = 'Tags'

print('\t'.join(COLUMNS))

for draws, gender in ((men,'m'), (wmn,'f')):
    count = draws.number_of_rows()
    for player in range(2, count):
        row = draws.row_at(player)
        if not row[0]: continue

        data = {}
        for k,i in cols.items():
            data[k] = row[i]
        data['Tags'] = f'{sys.argv[2]}-wl' if data['WL'] else f'{sys.argv[2]}'

        print("{Name}\t{First name}\t{Email}\t{Tags}".format(**data))

sys.exit(0)
