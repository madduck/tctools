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
known_players = {}

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

    cur_codes = {p.squash_code for p in data.get_players() if p.squash_code}

    for known_code, known_player in list(known_players.items()):
        if (
            known_code in cur_codes
            or known_player.player.name in known_players
        ):
            # The player is still registered
            continue

        # The player is no longer registered
        print(f"  Out: {known_player.player!r}", file=sys.stderr)
        del known_players[
            known_code
            if (known_code not in cur_codes)
            else known_player.player.name
        ]

    for player in data.get_players():
        code = player.squash_code
        known_player = known_players.get(code)
        if not known_player:
            if player.name in known_players:
                if player.squash_code:
                    # The player was previously registered without a squash code, so
                    # migrate
                    known_players[player.squash_code] = TimestampPlayer(
                        known_players[player.name].timestamp, player
                    )
                    del known_players[player.name]
                    print(
                        f"  Chg: {player!r} ({player.squash_code})",
                        file=sys.stderr,
                    )

            else:
                # The player is new
                print(
                    f"  New: {player!r} ({code or 'No code'})", file=sys.stderr
                )
                known_players[code or player.name] = TimestampPlayer(
                    timestamp, player
                )

        elif known_player.player != player:
            s1 = set((known_player.player.data | dict(id=None)).items())
            s2 = set((player.data | dict(id=None)).items())
            diff = [v[0] for v in s2 - s1 if not v[0].startswith("grad")]
            print(f"  Upd: {player!r} ({', '.join(diff)})", file=sys.stderr)
            known_players[code] = TimestampPlayer(
                known_player.timestamp, player
            )

known_players = sorted(
    known_players.values(), key=lambda p: (p.timestamp, -p.player.points)
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


def make_player_row(player, id=None):
    cols = [fn(player[DataSource.sanitise_colname(c)]) for c, fn in colnames]
    if id:
        cols[0] = id
    return cols


players_in = sorted(
    known_players[: args.cutoff], key=lambda p: -p.player.points
)
players_wl = sorted(
    known_players[args.cutoff :], key=lambda p: -p.player.points
)  # noqa:E203

if players_wl:
    print(f"\n{len(players_wl)} players moved to waiting list:")
    for i, p in enumerate(players_wl):
        print(f"   {i+1:3d}:{p.player!r} ({p.timestamp})")

print(f"\n{len(players_in)} players made the cut-off:")
for gender, title in (
    (Gender.W, "Women"),
    (Gender.M, "Men"),
    (Gender.N, "Ungendered"),
):
    cnt = 0
    for p in players_in:
        if p.player.gender != gender:
            continue
        elif cnt == 0:
            print(f"  {title}:")
        cnt += 1
        print(f"   {cnt:3d}:{p.player!r}")

if args.output:

    regs = pyexcel.Sheet(
        name="Registrations",
        colnames=[col[0] for col in colnames] + ["Timestamp"],
        sheet=[
            make_player_row(p.player, i + 1)
            + [p.timestamp.strftime("%F %H:%M:%S")]
            for i, p in enumerate(players_in)
        ],
    )

    sheets = {regs.name: regs}

    if args.cutoff < len(known_players):

        wl = pyexcel.Sheet(
            name="Waiting list",
            colnames=[col[0] for col in colnames] + ["Timestamp"],
            sheet=[
                make_player_row(p.player, i + 1)
                + [p.timestamp.strftime("%F %H:%M:%S")]
                for i, p in enumerate(players_wl)
            ],
        )

        if args.waitlist:
            outwl = pyexcel.Book(sheets={wl.name: wl})
            outwl = outwl.save_as(args.waitlist)

        else:
            sheets[wl.name] = wl

    outbook = pyexcel.Book(sheets=sheets)
    outbook.save_as(args.output)
