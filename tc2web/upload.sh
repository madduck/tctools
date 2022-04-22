#!/bin/sh
#
# upload.sh — push files to an FTP server
#
# This expects a file upload.creds in the local directory with the credentials
# to use for FTP access:
#
#   FTPUSER=username
#   FTPPASS=password
#   FTPHOST=ftp.example.org
#   TARGETDIR=/tc/
#
# Copyright © 2021–2022 martin f. krafft <m@rtin.kiwi>
# Released under the terms of the MIT Licence.
#
set -eu

FILES="display.css display.png display.html index.html live.html style.css"

cd "${0%/*}"

if [ -f .shasums ] && shasum -sc .shasums; then
  echo >&2 No changes.
  exit 0
fi

for f in $FILES; do
  shasum "$f" || echo "0  $f"
done > .shasums

if [ -r ./upload.creds ]; then
  . ./upload.creds
  exec ncftpput -u "$FTPUSER" -p "$FTPPASS" $FTPHOST ${TARGETDIR:-.} $FILES

else
  echo >&2 No upload.creds file, so cannot upload.
  exit 1
fi
