#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
from pytcnz.dtkapiti.tcexport_reader import TCExportReader
from pytcnz.squashnz.isquash_controller import iSquashController
from pytcnz.meta import epilog

parser = argparse.ArgumentParser(
    description="Automatically enter tournament results into iSquash"
)
parser.epilog = epilog

parser.add_argument(
    "--input",
    "-i",
    metavar="EXPORT_FILE",
    type=str,
    required=True,
    dest="spreadsheet",
    help="TC export file to read",
)
parser.add_argument(
    "--headless",
    action="store_true",
    dest="headless",
    help="Operate without a browser window (invisible)",
)
parser.add_argument(
    "--username",
    "-u",
    metavar="USERNAME",
    required=True,
    help="iSquash user name for login",
)
parser.add_argument(
    "--password",
    "-p",
    metavar="PASSWORD",
    required=True,
    help="iSquash password for login",
)
parser.add_argument(
    "--tournament",
    "-t",
    metavar="TOURNAMENT_CODE",
    required=True,
    help="iSquash tournament code",
)
parser.add_argument(
    "--draw",
    "-d",
    type=str,
    metavar="DRAW_CODE",
    action="append",
    help="Only enter given draw, or draws if given more than once, "
    'or "-" for none (i.e. just to publish to grading list).',
)
parser.add_argument(
    "--reset",
    action="store_true",
    dest="reset",
    help="Reset results for draw or draws to 0/0 ×5",
)
parser.add_argument(
    "--publish",
    action="store_true",
    dest="publish",
    help="Publish to grading list",
)
args = parser.parse_args()

data = TCExportReader(args.spreadsheet, add_games_to_draws=True)
data.read_draws()
data.read_games()

with iSquashController(headless=args.headless) as c:
    print(c, file=sys.stderr)
    c.go_login(args.username, args.password)
    print(c, file=sys.stderr)
    c.go_manage_tournament(args.tournament)
    print(c, file=sys.stderr)
    c.go_design_tournament()
    print(c, file=sys.stderr)

    for draw in data.draws.values():

        if args.draw:
            if args.draw == "-":
                break

            elif draw.name not in args.draw:
                continue

        done = []
        while True:
            print(
                f"  {draw!r} {len(done)} games already entered",
                file=sys.stderr,
            )
            entered = c.go_enter_results_for_draw(
                draw, done=done, reset=args.reset
            )
            if args.reset:
                print(f"  {draw!r} reset ({len(entered)} games)")
                break
            elif len(entered) + len(done) == len(draw.games):
                print(f"  {draw!r} done ({len(draw.games)} games)")
                break
            elif not entered:
                raise RuntimeError(f"Not making progress on draw {draw}")
            else:
                done.extend(entered)

    print(c, file=sys.stderr)

    if args.publish:
        c.go_send_to_gradinglist()

    c.go_logout()
    print(c, file=sys.stderr)