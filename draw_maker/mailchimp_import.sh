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
#   ./mailchimp_import.sh draw_maker.ods 2021-10-open | xclip -i
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#
set -eu

echo "Name	First name	Email	Tags"
${0%/*}/player_mmerge.py -a "$1" "{name}	{first name}	{email} $2{wl}" \
  | sed -e 's,False$,,;s,True$,-wl,'
