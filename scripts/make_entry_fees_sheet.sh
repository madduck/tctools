#!/bin/sh
set -eu

if [ -e "${0%/*}/tc-export-fixed.xls" ]; then
  set -- "${0%/*}/tc-export-fixed.xls"
fi

if [ ! -r "${1:-}" ]; then
  echo >&2 "Need the fixed TC export file as first argument, please"
  exit 1
fi

SELF="${0%.*}"
SELF="${SELF##*/}"
outfile=$(mktemp --tmpdir ${SELF}.XXXXXXXX.html)

./player_mmerge.py -t entry_fees_sheet.j2 --tcexport ${1:-} > $outfile
x-www-browser $outfile
