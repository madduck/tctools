#!/bin/sh
set -eu

./player_mmerge.py -t entry_fees_sheet.j2 ../tc-export-fixed.xls > entry_fees_sheet.html
x-www-browser entry_fees_sheet.html
