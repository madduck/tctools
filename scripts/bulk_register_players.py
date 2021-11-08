#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
from pytcnz.squashnz.gradinglist_reader import (
    GradingListReader,
    make_argument_parser as make_gl_argument_parser,
)
from pytcnz.squashnz.isquash_controller import (
    iSquashController,
    make_argument_parser as make_is_argument_parser,
)
from pytcnz.util import get_config_filename
from pytcnz.meta import epilog

data = GradingListReader()

gl_argparser = make_gl_argument_parser(
    gender_choices=data.gender_choices,
    age_choices=data.age_choices,
    grade_choices=data.grade_choices,
    sleep_default=5,
)

is_argparser = make_is_argument_parser(configfile=get_config_filename())

parser = argparse.ArgumentParser(
    description="Bulk-register players for a tournament",
    parents=[is_argparser, gl_argparser],
)
parser.epilog = epilog

args = parser.parse_args()

data.read_players(
    name=args.name,
    districts=args.district,
    clubs=args.club,
    genders=args.gender,
    ages=args.age,
    grades=args.grade,
    points_min=args.minpoints,
    points_max=args.maxpoints
)

with iSquashController(headless=args.headless, debug=args.debug) as c:
    print(c, file=sys.stderr)
    c.go_login(args.username, args.password)
    print(c, file=sys.stderr)
    c.go_manage_tournament(args.tournament)
    print(c, file=sys.stderr)

    def callback(player, added, *, error=False, msg=None):
        if error:
            print(f'  ERR: {player!r} "{msg}"')
        elif added:
            print(f"  Reg: {player!r} ({msg})")
        else:
            print(f"       {player!r} is already registered")

    c.go_fill_registrations(data.players.values(), player_cb=callback)
    print(c, file=sys.stderr)

    c.go_logout()
    print(c, file=sys.stderr)
