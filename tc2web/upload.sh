#!/bin/sh
set -eu

FILES="display.css display.png display.html index.html live.html style.css games.html schedule.html draws.html"

cd "${0%/*}"

if [ -f .shasums ] && shasum -sc .shasums; then
  echo >&2 No changes.
  exit 0
fi

shasum $FILES > .shasums

. ./upload.creds
exec ncftpput -u "$FTPUSER" -p "$FTPPASS" $FTPHOST ${TARGETDIR:-.} $FILES
