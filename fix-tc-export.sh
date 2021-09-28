#!/bin/sh
#
# fix-tc-export.sh tc-export.xls
#
# Fix a file exported from TournamentControl (which uses an ancient Excel
# format not supported by the tools here)
#

FILE="${1:-tc-export.xls}"
BASENAME="${FILE%.*}"

cd "${0%/*}"

if [ ! -r "$FILE" ]; then
  echo >&2 "No such file: $FILE"
  exit 1
fi

libreoffice --convert-to ods "$FILE"
mv "$BASENAME".ods "$BASENAME"-fixed.ods
libreoffice --convert-to xls "$BASENAME"-fixed.ods
rm "$BASENAME"-fixed.ods

echo >&2 "File fixed and left as $BASENAME-fixed.xls"