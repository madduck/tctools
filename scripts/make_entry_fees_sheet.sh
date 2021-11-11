#!/bin/sh
set -eu

MYDIR="${0%/*}"

if [ -e "$MYDIR/../tc-export-fixed.xls" ]; then
  set -- "$MYDIR/../tc-export-fixed.xls"
fi

if [ ! -r "${1:-}" ]; then
  echo >&2 "Need the fixed TC export file as first argument, please"
  exit 1
fi

SELF="${0%.*}"
SELF="${SELF##*/}"
outfile=$(mktemp --tmpdir ${SELF}.XXXXXXXX.html)

"$MYDIR"/player_mmerge.py -t "$MYDIR"/entry_fees_sheet.j2 --tcexport ${1:-} > $outfile
xdg-open $outfile
