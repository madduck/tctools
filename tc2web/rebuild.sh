#!/bin/sh
#
# rebuild.sh — rebuild the HTML files
#
# Copyright © 2021–2022 martin f. krafft <m@rtin.kiwi>
# Released under the terms of the MIT Licence.
#
set -eu

for i in "${1:-../tc-export-fixed.xls}" ../tc-export-demo.xls; do
  if [ -r "$i" ]; then
    FILE="$i"
    break
  fi
done

case "$FILE" in
  (*-demo.xls) echo >&2 WARNING: Running on demo data ;;
  ('')
    echo >&2 No input file specified, aborting.
    exit 1
    ;;
esac

exec "${0%/*}/tc2web.py" --input "$FILE" --template live.j2 --output live.html
