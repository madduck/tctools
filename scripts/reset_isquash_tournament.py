#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
from pytcnz.squashnz.isquash_controller import (
    iSquashController,
    make_argument_parser as make_is_argument_parser,
)
from pytcnz.meta import epilog

is_argparser = make_is_argument_parser(configfile=get_config_filename())

parser = argparse.ArgumentParser(
    description="Delete draws and registrations for a tournament",
    parents=[is_argparser],
)
parser.epilog = epilog

parser.add_argument(
    "--draws",
    action="store_true",
    dest="draws",
    help="Delete all draws",
)

parser.add_argument(
    "--players",
    action="store_true",
    dest="players",
    help="""
        Unregister all players (only unassigned players if specified without
        draws.
    """
)

parser.add_argument(
    "--force",
    action="store_true",
    dest="force",
    help="Do not ask for confirmation."
)

args = parser.parse_args()

if not args.force:
    confirmstring = 'YES SURE'
    ans = input(f"Type {confirmstring} to continue: ")
    if not ans == confirmstring:
        print("Bailing out then…", file=sys.stderr)
        sys.exit(1)

with iSquashController(headless=args.headless, debug=args.debug) as c:
    print(c, file=sys.stderr)
    c.go_login(args.username, args.password)
    print(c, file=sys.stderr)
    c.go_manage_tournament(args.tournament)
    print(c, file=sys.stderr)

    if args.draws:

        def callback(draw_name):
            print(f"  {draw_name} deleted", file=sys.stderr)

        c.go_delete_draws(None, draw_cb=callback)

    if args.players:

        def callback(name, removed=True, *, msg=None):
            if removed:
                print(f"      {name} unregistered")
            else:
                print(f"  ERR {name}: {msg}")

        c.go_clear_registrations(player_cb=callback)
