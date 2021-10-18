#!/bin/sh
#
# mailchimp_import.sh
#
# Exports all players including waitlisted players to a
# simple TSV format suitable for Mailchimp import. The second
# argument is the tag base, and '-wl' will be appended for
# players on the waiting list.
#
# Usage:
#   ./mailchimp_import.sh draw_maker.ods 2021-10-open
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
set -eu

if ! command -v xclip >/dev/null; then
  echo >&2 "I need xclip installed. Please install it."
  exit 1
fi

if [ ! -r "${1:-}" ]; then
  echo >&2 "Need the DrawMaker file as first argument, please"
  exit 1

elif [ -z "${2:-}" ]; then
  echo >&2 "Provide a tag base, please, like 2021-10-open"
  exit 1
fi

{
  echo "Name	First name	Email	Tags"
  ${0%/*}/player_mmerge.py --drawmaker "$1" --all \
    "{name}	{first_name}	{email} $2{wl:d}" \
    | sed -e 's,0$,,;s,1$,-wl,'
} | xclip -i -selection clipboard

xclip -o -selection clipboard | echo "$(wc -l) records ready in the clipboard."
echo "Now go to Mailchimp, Audience, Import, Cut-n-paste, and hit Ctrl-v."
