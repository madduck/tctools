#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
import datetime
from pytcnz.tctools.drawmaker_reader import DrawsReader
from pytcnz.squashnz.isquash_controller import (
    iSquashController,
    DRAW_TYPES,
    make_argument_parser as make_is_argument_parser,
)
from pytcnz.meta import epilog

is_argparser = make_is_argument_parser()

parser = argparse.ArgumentParser(
    description="Manage tournaments on iSquash",
    parents=[is_argparser],
)
parser.epilog = epilog

inputg = parser.add_argument_group(title="Input")
inputg.add_argument(
    "--input",
    "-i",
    metavar="DRAWMAKER_FILE",
    type=str,
    dest="drawmaker",
    help="DrawMaker file to read",
)

opsg = parser.add_argument_group(
    title="Operations",
    description="""
        The main operations relating to managing tournaments on iSquash.
        All of these can be combined, or run individually, as needed.
    """,
)

opsg.add_argument(
    "--register",
    action="store_true",
    dest="register",
    help="Ensure all players are registered for the draws being processed",
)

regg = parser.add_argument_group(
    title="Registering players",
    description="These options only make sense in the presence of --register",
)
regg.add_argument(
    "--update",
    action="store_true",
    dest="update",
    help="Update player comments for registered players",
)

opsg.add_argument(
    "--seed",
    action="store_true",
    dest="seedregs",
    help="""
        Adjust the grading list points for ALL players. It is not possible
        to do this just for a subset, or per-draw. Use with care. If you
        need to override grading points for a player, you will need to do
        this manually for now.
    """,
)
opsg.add_argument(
    "--extract-registrations",
    type=str,
    metavar="REGISTRATIONS_FILE",
    dest="extractregs",
    help="Extract registrations file when done",
)
opsg.add_argument(
    "--delete",
    action="store_true",
    dest="deldraws",
    help="""
        Delete draw or draws. Run this before making them if there were
        structural changes. Draws with results entered already cannot be
        deleted.
    """,
)
opsg.add_argument(
    "--make",
    action="store_true",
    dest="makedraws",
    help="Make draws that do not exist yet, or which have been deleted.",
)

makeg = parser.add_argument_group(
    title="Making draws",
    description="These options only make sense in the presence of --make",
)
makeg.add_argument(
    "--draw-type",
    "-y",
    metavar="DRAW=TYPE",
    action="append",
    dest="drawtypemap",
    help="Specify types for draws, e.g. M4=6b; "
    f'Choices: {", ".join(DRAW_TYPES.keys())}',
)
makeg.add_argument(
    "--draw-desc",
    "-n",
    metavar="DRAW=DESC",
    action="append",
    dest="drawdescmap",
    help='Override long descriptions for draws, e.g. M4="Mens 4th Division"',
)

opsg.add_argument(
    "--populate",
    action="store_true",
    dest="populate",
    help="Populate draws with players. This will also initialise the matches.",
)
opsg.add_argument(
    "--extract-draws",
    type=str,
    metavar="DRAWS_FILE",
    dest="extractdraws",
    help="Extract draws file when done.",
)
opsg.add_argument(
    "--update-web",
    action="store_true",
    dest="updateweb",
    help="Update Web diagram when done",
)

limitg = parser.add_argument_group(
    title="Limiting", description="Use these options to limit operations"
)
limitg.add_argument(
    "--draw",
    "-d",
    type=str,
    metavar="DRAW_CODE",
    dest="draws",
    action="append",
    help="""
        Only operate on the given draw,
        or draws if specified more than once
    """,
)

args = parser.parse_args()

if not args.makedraws and (args.drawtypemap or args.drawdescmap):
    parser.error("--draw-type and --draw-desc only make sense with --make")

if not args.register and args.update:
    parser.error("--update only makes sense with --register")

data = None
if args.register or args.makedraws or args.populate:
    if args.drawmaker:
        data = DrawsReader(args.drawmaker, add_players_to_draws=True)
        data.read_draws()
        data.read_players()
    else:
        parser.error(
            "Must specify DrawMaker spreadsheet to read using --input/-i"
        )

drawtypemap = {}
for pair in args.drawtypemap or ():
    d, t = pair.split("=")
    if t not in DRAW_TYPES:
        parser.error(f"Invalid draw type: {t}", file=sys.stderr)
    drawtypemap[d] = t

drawdescmap = {}
for pair in args.drawdescmap or ():
    d, t = pair.split("=")
    drawtypemap[d] = t


def timestamp_filename(filename):
    return filename.replace(
        "TIMESTAMP", datetime.datetime.now().strftime("%F-%H-%M-%S")
    )


with iSquashController(headless=args.headless, debug=args.debug) as c:
    print(c, file=sys.stderr)
    c.go_login(args.username, args.password)
    print(c, file=sys.stderr)
    c.go_manage_tournament(args.tournament)
    print(c, file=sys.stderr)

    if args.register:
        if args.draws:
            players = [
                p for p in data.players.values() if p.draw.name in args.draws
            ]
        else:
            players = data.players.values()

        def callback(player, added, *, error=False, msg=None):
            if error:
                print(f'  ERR: {player!r} "{msg}"')
            elif added:
                print(f"  Reg: {player!r} ({msg})")
            else:
                print(f"       {player!r} is already registered")

        c.go_fill_registrations(
            players, update=args.update, player_cb=callback
        )
        print(c, file=sys.stderr)

    if args.seedregs:
        c.go_seed_tournament()
        print(c, file=sys.stderr)

    if args.extractregs:
        filename = timestamp_filename(args.extractregs)
        print(
            f"  Extracting registrations to {filename} …",
            file=sys.stderr,
        )
        c.go_extract_registrations(filename)
        print(c, file=sys.stderr)

    if args.deldraws:

        def callback(draw_name):
            draw_name = (
                repr(data.draws.get(draw_name, draw_name))
                if data
                else draw_name
            )
            print(f"  {draw_name} deleted", file=sys.stderr)

        c.go_delete_draws(args.draws, draw_cb=callback)
        print(c, file=sys.stderr)

    if args.makedraws or args.populate:
        for draw in data.draws.values():
            if args.draws:
                if args.draws == "-":
                    break

                elif draw.name not in args.draws:
                    continue

            if args.makedraws:
                drawtype = drawtypemap.get(draw.name)
                if not drawtype:
                    lng = len(draw.players)
                    if lng in (8, 16, 32):
                        drawtype = str(lng)  # noqa:E271,E701,E501
                    elif lng in (4, 5):
                        drawtype = f"{lng}rr"  # noqa:E701
                    elif lng in (6,):
                        drawtype = f"{lng}b"  # noqa:E701
                    else:
                        print(
                            "Cannot determine draw type for draw {draw}",
                            file=sys.stderr,
                        )
                        sys.exit(1)

                print(
                    f"  {draw!r}, creating with type {drawtype}",
                    file=sys.stderr,
                )
                c.go_add_draw(
                    draw,
                    drawtype=drawtype,
                    drawdesc=drawdescmap.get(draw.name),
                )
                print(c, file=sys.stderr)

            if args.populate:
                print(f"  {draw!r}, populating…", file=sys.stderr)

                def callback(idx, player, isqname):
                    print(
                        f"    {idx+1:2d} {isqname} for {player!r}",
                        file=sys.stderr,
                    )

                c.go_seed_draw(draw, player_cb=callback)

                print(f"  {draw!r}, match making…", file=sys.stderr)
                c.go_make_matches_for_draw(draw)
                print(c, file=sys.stderr)

    if args.extractdraws:
        filename = timestamp_filename(args.extractdraws)
        print(
            f"  Extracting draws to {filename} (takes a while)…",
            file=sys.stderr,
        )
        c.go_extract_draws(filename)
        print(c, file=sys.stderr)

    if args.updateweb:
        print("  Updating web diagrams…", file=sys.stderr)
        c.go_update_web_diagram()
        print(c, file=sys.stderr)

    c.go_logout()
    print(c, file=sys.stderr)
