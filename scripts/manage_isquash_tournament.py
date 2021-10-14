#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import argparse
import sys
from pytcnz.tctools.drawmaker_reader import DrawsReader
from pytcnz.squashnz.isquash_controller import iSquashController, \
        DRAW_TYPES, make_argument_parser as make_is_argument_parser
from pytcnz.meta import epilog

is_argparser = make_is_argument_parser()

parser = argparse.ArgumentParser(
    description='Automatically create and seed draws on iSquash',
    parents=[is_argparser])
parser.epilog = epilog

parser.add_argument('--input', '-i', metavar='DRAWMAKER_FILE', type=str,
                    dest="spreadsheet", help='DrawMaker file to read')

subparsers = parser.add_subparsers(
    title='Available operations',
    description="Use these sub-commands to manage registrations, or draws",
    help="""Run e.g. `%(prog)s regs --help` for help on managing
            registrations, and `%(prog)s regs --help` for draws. Note that the
            common options shown in `%(prog)s --help` still apply, especially
            the required ones.""")
regp = subparsers.add_parser('regs')
drawp = subparsers.add_parser('draws')

regp.add_argument(
    '--clear', action="store_true", dest="clearregs",
    help='Unregister ALL players (does not respect --draw)')
regp.add_argument(
    '--register', action="store_true", dest='register',
    help='Ensure that all players are registered')
regp.add_argument(
    '--sleep', type=int, dest='sleep', default=0,
    help='Sleep between registrations so as to not overload iSquash')
regp.add_argument(
    '--update', action="store_true", dest='update',
    help='Update player comments for registered players')
regp.add_argument(
    '--draw', '-d', type=str, metavar='DRAW_CODE', dest="draws",
    action="append",
    help='Only register players in the given draw, '
         'or draws if specified more than once')

drawp.add_argument(
    '--draw', '-d', type=str, metavar='DRAW_CODE', dest="draws",
    action="append",
    help='Only operate on the given draw, '
         'or draws if specified more than once')
drawp.add_argument(
    '--delete', action="store_true", dest="deldraws",
    help='Delete draw or draws first, where possible')
drawp.add_argument(
    '--make', action="store_true", dest="makedraws",
    help='Make draws that do not exist yet')
makeg = drawp.add_argument_group(
    title='Making draws',
    description='These options only make sense in the presence of --make')
makeg.add_argument(
    '--draw-type', '-y', metavar='DRAW=TYPE', action="append",
    dest="drawtypemap",
    help='Specify types for draws, e.g. M4=6b; '
         f'Choices: {", ".join(DRAW_TYPES.keys())}')
makeg.add_argument(
    '--draw-desc', '-n', metavar='DRAW=DESC', action="append",
    dest="drawdescmap",
    help='Override long descriptions for draws, e.g. M4="Mens 4th Division"')
drawp.add_argument(
    '--seed', action="store_true", dest="seeddraws",
    help='Seed draws with players')
drawp.add_argument(
    '--update-web', action="store_true", dest="webupdate",
    help='Update Web diagram when done')

args = parser.parse_args(namespace=argparse.Namespace(
    makedraws=False,
    deldraws=False,
    seeddraws=False,
    webupdate=False,
    clearregs=False,
    register=False,
    drawtypemap=[],
    drawdescmap=[],
    ))

if not args.makedraws and (args.drawtypemap or args.drawdescmap):
    parser.error('--draw-type and --draw-desc only make sense with --make',
                 file=sys.stderr)

if args.spreadsheet:
    data = DrawsReader(args.spreadsheet, add_players_to_draws=True)
    data.read_draws()
    data.read_players()
elif args.makedraws or args.register or args.seeddraws:
    parser.error('Must specify DrawMaker spreadsheet to read using --input/-i')
else:
    data = None

drawtypemap = {}
for pair in args.drawtypemap or ():
    d, t = pair.split('=')
    if t not in DRAW_TYPES:
        parser.error(f"Invalid draw type: {t}", file=sys.stderr)
    drawtypemap[d] = t

drawdescmap = {}
for pair in args.drawdescmap or ():
    d, t = pair.split('=')
    drawtypemap[d] = t

with iSquashController(headless=args.headless, debug=args.debug) as c:
    print(c, file=sys.stderr)
    c.go_login(args.username, args.password)
    print(c, file=sys.stderr)
    c.go_manage_tournament(args.tournament)
    print(c, file=sys.stderr)

    if args.clearregs:
        def callback(name, removed=True, *, msg=None):
            if removed:
                print(f'      {name} unregistered')
            else:
                print(f'  ERR {name}: {msg}')

        c.go_clear_registrations(player_cb=callback)

    if args.register:
        if args.draws:
            players = [p for p in data.players.values()
                       if p.draw.name in args.draws]
        else:
            players = data.players.values()

        def callback(player, added, *, error=False, msg=None):
            if error:
                print(f'  ERR: {player!r} "{msg}"')
            elif added:
                print(f"  Reg: {player!r} ({msg})")
            else:
                print(f"       {player!r} is already registered")

        c.go_fill_registrations(players, update=args.update, sleep=args.sleep,
                                player_cb=callback)
        print(c, file=sys.stderr)

    if args.deldraws:
        def callback(draw_name):
            if data:
                print(f'  {data.draws[draw_name]!r} deleted',
                      file=sys.stderr)
            else:
                print(f'  {draw_name} deleted', file=sys.stderr)

        c.go_delete_draws(args.draws, draw_cb=callback)

    if args.makedraws or args.seeddraws:
        for draw in data.draws.values():
            if args.draws:
                if args.draws == '-':
                    break

                elif draw.name not in args.draws:
                    continue

            if args.makedraws:
                drawtype = drawtypemap.get(draw.name)
                if not drawtype:
                    lng = len(draw.players)
                    if   lng in (8, 16, 32): drawtype = str(lng)    # noqa:E271,E701,E501
                    elif lng in (4, 5):      drawtype = f'{lng}rr'  # noqa:E701
                    elif lng in (6,):        drawtype = f'{lng}b'   # noqa:E701
                    else:
                        print("Cannot determine draw type for draw {draw}",
                              file=sys.stderr)
                        sys.exit(1)

                print(f'  {draw!r}, creating with type {drawtype}',
                      file=sys.stderr)
                c.go_add_draw(draw, drawtype=drawtype,
                              drawdesc=drawdescmap.get(draw.name))

            if args.seeddraws:
                print(f'  {draw!r}, seeding…', file=sys.stderr)

                def callback(idx, player, isqname):
                    print(f'    {idx+1:2d} {isqname} for {player!r}',
                          file=sys.stderr)
                c.go_seed_draw(draw, player_cb=callback)

                print(f'  {draw!r}, match making…', file=sys.stderr)
                c.go_make_matches_for_draw(draw)

    if args.webupdate:
        c.go_update_web_diagram()

    print(c, file=sys.stderr)

    c.go_logout()
    print(c, file=sys.stderr)
