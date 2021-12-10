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
    make_argument_parser,
)
from pytcnz.meta import epilog

data = GradingListReader()

gl_argparser = make_argument_parser(
    gender_choices=data.gender_choices,
    age_choices=data.age_choices,
    grade_choices=data.grade_choices,
    sleep_default=5,
)

parser = argparse.ArgumentParser(
    description="Search the SquashNZ grading list", parents=[gl_argparser]
)
parser.epilog = epilog

parser.add_argument(
    "--separator",
    "-S",
    metavar="SEPARATOR",
    type=str,
    default="\t",
    help="Separator to use between fields in default template, "
    "available also as {separator}",
)
parser.add_argument(
    "--list",
    "-l",
    metavar="CATEGORY",
    type=str,
    choices=('districts', 'clubs', 'ages', 'grades'),
    help="List all known entities in the given category",
)
parser.add_argument(
    "--force",
    "-f",
    action="store_true",
    help="Separator to use between fields in default template, "
    "available also as {separator}",
)
parser.add_argument(
    "template",
    metavar="TEMPLATE_TEXT",
    type=str,
    nargs="*",
    help="Template text to use to display results. "
    "Available fields: id,code,name,gender,grade,points; "
    "Example: '{name} {points}'",
)

args = parser.parse_args()

if args.list:
    try:
        print('\n'.join(f"{k}: {v}" for k, v in getattr(data, args.list).items()))
    except AttributeError:
        print('\n'.join(getattr(data, args.list)))
    sys.exit(0)

if not (args.district or args.club) and not args.force and not args.name:
    parser.error("Will not search all districts/clubs without --force")

data.read_players(
    name=args.name,
    districts=args.district,
    clubs=args.club,
    genders=args.gender,
    ages=args.age,
    grades=args.grade,
    points_min=args.minpoints,
    points_max=args.maxpoints,
    colmap=dict(squash_code="code"),
)

if args.template:
    template = " ".join(args.template)
else:
    template = "{separator}".join(
        f"{{{f}}}"
        for f in ("code", "name", "gender", "grade", "points", "club")
    )

for player in data.players.values():
    try:
        print(player.fill_template(template, separator=args.separator))

    except KeyError as e:
        parser.error(e)
