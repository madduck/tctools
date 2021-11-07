#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import re
import glob
import os.path
import argparse
import functools
import pyexcel
import datetime
from collections import namedtuple
from pytcnz.meta import epilog
from pytcnz.gender import Gender
from pytcnz.squashnz.player import Player
from pytcnz.squashnz.registrations_reader import (
    RegistrationsReader,
    DataSource,
)
from pytcnz.datasource import DataSource

parser = argparse.ArgumentParser(
    description="Move late entries to waiting list"
)
parser.epilog = epilog

parser.add_argument(
    "--cutoff",
    "-c",
    required=True,
    type=int,
    help="Split-off to waiting list after NUMBER players",
)
parser.add_argument(
    "--output",
    "-o",
    metavar="REGISTRATIONS_FILE",
    type=str,
    help="Registrations file to write",
)
parser.add_argument(
    "--waitlist",
    "-w",
    metavar="WAITLIST_FILE",
    type=str,
    help="""
        Separate waitlist file to write
        (else waitlist becomes a separate tab in the output file)
    """,
)
parser.add_argument(
    "registrations_file",
    nargs="+",
    type=str,
    help="Extracted registrations.xls files to process",
)

args = parser.parse_args()

TimestampPlayer = namedtuple("TimestampPlayer", ["timestamp", "player"])
players = {}

files = sorted(
    functools.reduce(
        lambda a, i: a + glob.glob(i), args.registrations_file, []
    )
)

for regfile in files:
    basename = os.path.basename(regfile)
    stampstr = re.match(r"^\d{4}(?:-\d{2}){5}", basename)
    if stampstr:
        timestamp = datetime.datetime.strptime(
            stampstr[0], "%Y-%m-%d-%H-%M-%S"
        )
    else:
        print(f"Cannot parse timestamp from {basename}", file=sys.stderr)
        sys.exit(1)

    print(
        "Processing registrations as per "
        f"{timestamp.strftime('%a %F %H:%M')}",
        file=sys.stderr,
    )

    data = RegistrationsReader(regfile, Player_class=Player)
    try:
        data.read_players(strict=False)

    except DataSource.ReadError as e:
        print(f"In file {regfile}: {e}", file=sys.stderr)
        continue

    codes = {p.squash_code for p in data.get_players()}

    for code, player in list(players.items()):
        if code not in codes:
            # The player is no longer registered
            print(f"  Out: {player.player!r}", file=sys.stderr)
            del players[code]

    for player in data.get_players():
        known = players.get(player.squash_code)
        if not known:
            # The player is new
            print(f"  New: {player!r}", file=sys.stderr)
            players[player.squash_code] = TimestampPlayer(timestamp, player)

        elif known.player != player:
            s1 = set((known.player.data | dict(id=None)).items())
            s2 = set((player.data | dict(id=None)).items())
            diff = [v[0] for v in s2 - s1 if not v[0].startswith("grad")]
            print(f"  Upd: {player!r} ({', '.join(diff)})", file=sys.stderr)
            players[player.squash_code] = TimestampPlayer(
                known.timestamp, player
            )

players = sorted(
    players.values(), key=lambda p: (p.timestamp, -p.player.points)
)
colnames = [
    ("ID", int),
    ("Name", str),
    ("Gender", Gender.to_sex),
    ("Squash Code", str),
    ("Points", int),
    ("DOB", lambda d: d.strftime("%d-%b-%Y") if d else ""),
    ("Phone", str),
    ("Mobile", str),
    ("Email", str),
    ("Comments", str),
]


def make_player_row(player):
    return [fn(player[DataSource.sanitise_colname(c)]) for c, fn in colnames]


players_in = sorted(players[: args.cutoff], key=lambda p: -p.player.points)
players_wl = sorted(
    players[args.cutoff :], key=lambda p: -p.player.points
)  # noqa:E203

if players_wl:
    print(f"\n{len(players_wl)} players moved to waiting list:")
    for i, p in enumerate(players_wl):
        print(f"   {i:3d}:{p.player!r}")

print(f"\n{len(players_in)} players made the cut-off:")
for gender, title in (
    (Gender.W, "Women"),
    (Gender.M, "Men"),
    (Gender.N, "Ungendered"),
):
    print(f"  {title}:")
    cnt = 0
    for p in players_in:
        if p.player.gender != gender:
            continue
        cnt += 1
        print(f"   {cnt:3d}:{p.player!r}")

if args.output:

    regs = pyexcel.Sheet(
        name="Registrations",
        colnames=[col[0] for col in colnames] + ["Timestamp"],
        sheet=[
            make_player_row(p.player) + [p.timestamp.strftime("%F %H:%M:%S")]
            for p in players_in
        ],
    )

    sheets = {regs.name: regs}

    if args.cutoff < len(players):

        wl = pyexcel.Sheet(
            name="Waiting list",
            colnames=[col[0] for col in colnames] + ["Timestamp"],
            sheet=[
                make_player_row(p.player)
                + [p.timestamp.strftime("%F %H:%M:%S")]
                for p in players_wl
            ],
        )

        if args.waitlist:
            outwl = pyexcel.Book(sheets={wl.name: wl})
            outwl = outwl.save_as(args.waitlist)

        else:
            sheets[wl.name] = wl

    outbook = pyexcel.Book(sheets=sheets)
    outbook.save_as(args.output)
