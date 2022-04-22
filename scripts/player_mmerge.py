#!/usr/bin/python3
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
import os
from pytcnz.dtkapiti.tcexport_reader import TCExportReader
from pytcnz.tctools.drawmaker_reader import DrawMakerReader, DrawsReader
from pytcnz.squashnz.registrations_reader import RegistrationsReader
from pytcnz.gender import Gender
from pytcnz.util import get_timestamp
import pytcnz.meta as META

try:
    import jinja2

    HAVE_JINJA2 = True
except ImportError:
    HAVE_JINJA2 = False

parser = argparse.ArgumentParser(description='"Mail"-merge player data')
parser.epilog = META.epilog

inputg = parser.add_argument_group(title="Input")
insheets = inputg.add_mutually_exclusive_group(required=True)
insheets.add_argument(
    "--registrations",
    metavar="REGISTRATIONS",
    type=str,
    dest="registrations",
    help="iSquash registrations file to read",
)
insheets.add_argument(
    "--tcexport",
    metavar="TC-EXPORT",
    type=str,
    dest="tcexport",
    help="TC export file to read",
)
insheets.add_argument(
    "--drawmaker",
    metavar="DRAWMAKER",
    type=str,
    dest="drawmaker",
    help="DrawMaker file to read",
)

inputg.add_argument(
    "--all",
    "-a",
    action="store_true",
    help="Read all players, not just those in draws",
)

inputg.add_argument(
    "--include-unavailable",
    action="store_true",
    help="Include players marked unavailable",
)

outputg = parser.add_argument_group(title="Output")
outdata = outputg.add_mutually_exclusive_group(required=False)
outdata.add_argument(
    "text",
    metavar="TEMPLATE_TEXT",
    type=str,
    nargs="*",
    default="",
    help="Template text to use for merge",
)
outdata.add_argument(
    "--file",
    "-f",
    metavar="FILE",
    default=None,
    type=str,
    help="File to read template text from",
)
if HAVE_JINJA2:
    outdata.add_argument(
        "--template",
        "-t",
        metavar="TEMPLATE",
        default=None,
        type=str,
        help="Jinja2 template to be used for the merge",
    )


filterg = parser.add_argument_group(title="Filters")
filterg.add_argument(
    "--waitlist",
    "-w",
    action="store_true",
    dest="waitlist",
    help="Limit to players on waitlist (see also --all)",
)
filterg.add_argument(
    "--gender",
    "-g",
    type=str,
    metavar="GENDER",
    choices=["m", "f"],
    dest="gender",
    default=None,
    help="Limit to players of the specified gender",
)
filterg.add_argument(
    "--code",
    "-c",
    type=str,
    metavar="CODE",
    dest="code",
    help="Limit to players whose codes start with CODE",
)
filterg.add_argument(
    "--points",
    "-p",
    type=str,
    metavar="FROM-TO",
    default=None,
    help="Limit to players within points range",
)
filterg.add_argument(
    "--invert",
    "-i",
    action="store_true",
    dest="invert",
    default=False,
    help="Invert the filter criteria",
)
parser.add_argument(
    "--tournament_name",
    metavar="TOURNAMENT_NAME",
    type=str,
    help=("Tournament name to override data from source"),
)
parser.add_argument(
    "--separator",
    "-S",
    metavar="SEPARATOR",
    type=str,
    default="\t",
    help=(
        "Separator to use between fields in default template, available also"
        " as {separator}"
    ),
)

args = parser.parse_args(namespace=argparse.Namespace(template=None))

if args.file or args.template:
    f = args.file or args.template
    try:
        with open(f, "r") as inp:
            template = inp.read().strip()
    except FileNotFoundError as e:
        print(f"{e.strerror}: {e.filename}", file=sys.stderr)
        sys.exit(1)

elif args.template and args.separator:
    parser.error("Cannot use --separator/-S with --template/-t")

elif not args.template:
    if args.text:
        template = " ".join(args.text)
    else:
        fields = ("name", "gender", "grading.points", "age_group")
        template = "{separator}".join(f"{{{n}}}" for n in fields)

colmap = None
if args.tcexport:
    if args.include_unavailable or args.waitlist or args.all:
        print(
            "--all, --waitlist, and --include-unavailable make no sense with --tcexport",
            file=sys.stderr,
        )
        sys.exit(1)
    data = TCExportReader(args.tcexport)

elif args.drawmaker:
    if args.all:
        data = DrawMakerReader(args.drawmaker)
    else:
        data = DrawsReader(args.drawmaker, add_players_to_draws=True)
        data.read_draws()
    colmap = dict(squash_code="code")

elif args.registrations:
    if args.include_unavailable or args.waitlist or args.all:
        print(
            "--all, --waitlist, and --include-unavailable make no sense with --registrations",
            file=sys.stderr,
        )
        sys.exit(1)
    if not args.tournament_name:
        print(
            "--registrations requires --tournament_name",
            file=sys.stderr,
        )
        sys.exit(1)
    data = RegistrationsReader(args.registrations)
    colmap = dict(squash_code="code")

if args.tournament_name:
    data.set_tournament_name(args.tournament_name)
else:
    data.read_tournament_name()


def resolve_duplicate_cb(existing, new):
    # If a player is in the draw maker multiple times because e.g. on waitlist
    # and regularly registered, then make sure that we don't let a waitlist or
    # unavailable entry overwrite an existing one, and replace an existing one
    # if the new one is better
    if not new.wl and new.available:
        return new
    else:
        return existing


data.read_players(
    colmap=colmap, strict=False, resolve_duplicate_cb=resolve_duplicate_cb
)

if args.points:
    p = args.points.split("-")
    points_min = int(p[0])
    points_max = int(p[1]) if len(p) > 1 else points_min

else:
    points_min = 0
    points_max = -1

gender = Gender.N
if args.gender:
    gender = Gender.from_string(args.gender)

resultset = []
for player in data.players.values():

    if gender is not Gender.N:
        if (gender == player.gender) == args.invert:
            continue

    if not player.get("available", True) and not args.include_unavailable:
        continue

    if not args.invert:
        if args.code and not player.code.startswith(args.code):
            continue
        elif args.points and (
            player.points < points_min or player.points > points_max
        ):
            continue
        elif args.waitlist and not player.wl:
            continue

    else:
        if args.code and player.code.startswith(args.code):
            continue
        elif args.points and (
            player.points >= points_min and player.points <= points_max
        ):
            continue
        elif args.waitlist and player.wl:
            continue

    resultset.append(player)

if not args.template:

    for player in resultset:
        try:
            print(
                player.fill_template(
                    template,
                    separator=args.separator,
                    tournament_name=data.get_tournament_name(),
                )
            )

        except KeyError as e:
            parser.error(e)

else:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.getcwd()),
        autoescape=jinja2.select_autoescape(["j2"]),
    )
    template = env.from_string(template)
    print(
        template.render(
            meta=META,
            tournament_name=data.get_tournament_name(),
            timestamp=get_timestamp(),
            dataset=resultset,
        )
    )
