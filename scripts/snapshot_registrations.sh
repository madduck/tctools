#!/bin/sh
#
# snapshot_registrations.sh
#
# Usage:
#   ./snapshot_registrations.sh 80 regs.ods
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
set -eu

case "${1:-}" in
  (*[!0-9]*) echo >&2 "First argument needs to be numeric: $1"; exit 1;;
  ('') echo >&2 "Must specify cut-off point first"; exit 1;;
esac

DIR="${0%/*}"

SNAPSHOTDIR=$(realpath -e --relative-base="$PWD" "$DIR"/../snapshots)
"$DIR"/manage_isquash_tournament.py --headless \
  --extract-registrations "$SNAPSHOTDIR"/TIMESTAMP-registrations.xls

ls -1 "$SNAPSHOTDIR"/*-registrations.xls | while read f; do
  cur=$(md5sum "$f" | cut -d' ' -f1)
  if [ "$cur" = "${last:-}" ]; then
    echo >&2 "No changes since last snapshot."
    rm "$f"
  fi
  last="$cur"
done

exec "$DIR"/split_off_waitinglist.py --cutoff $1${2:+ --output $2} \
  "$SNAPSHOTDIR"/*-registrations.xls
