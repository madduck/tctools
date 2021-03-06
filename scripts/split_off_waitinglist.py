#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
# Released under the MIT Licence
#

import sys
import re
import glob
import os.path
import argparse
import configparser
import functools
import pyexcel
import datetime
from collections import namedtuple
from pytcnz.meta import epilog
from pytcnz.gender import Gender
from pytcnz.squashnz.player import Player as BasePlayer
from pytcnz.squashnz.registrations_reader import (
    RegistrationsReader,
    DataSource,
)
from pytcnz.util import get_config_filename
from pytcnz.datasource import DataSource

parser = argparse.ArgumentParser(
    description="Move late entries to waiting list"
)
parser.epilog = epilog

config = configparser.ConfigParser()
config.read(get_config_filename())
if config.has_section("split_off_waitinglist"):
    include = config["split_off_waitinglist"].get("include", "").split()
    codemap = dict(
        i.split("=", 1)
        for i in config["split_off_waitinglist"].get("codemap", "").split()
    )
else:
    include, codemap = [], []

parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Be verbose while parsing registration files",
)
parser.add_argument(
    "--cutoff",
    "-c",
    required=True,
    type=int,
    help="Split-off to waiting list after NUMBER players",
)
parser.add_argument(
    "--include",
    "-i",
    metavar="CODE",
    action="append",
    default=include,
    type=str,
    help="Ensure these players don't end up on the waiting list",
)
parser.add_argument(
    "--map",
    "-m",
    metavar="CODE=CODE",
    action="append",
    dest="codemap",
    default=codemap,
    type=str,
    help="Map old grading codes to new ones",
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
    "--delete-nodiff",
    "-d",
    action="store_true",
    dest="delete",
    help="Delete registrations files that add no new information",
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


class Player(BasePlayer):
    def __str__(self):
        return (
            f"{self.grading.points:4d} {self.grading.grade:2s} "
            f"{self.get_age_group()} {(self.squash_code or 'No code'):7s}  "
            f"{self.name}"
        )


files = sorted(
    functools.reduce(
        lambda a, i: a + glob.glob(i), args.registrations_file, []
    )
)

for regfile in files:
    changecount = 0
    basename = os.path.basename(regfile)
    stampstr = re.match(r"^\d{4}(?:-\d{2}){5}", basename)
    if stampstr:
        timestamp = datetime.datetime.strptime(
            stampstr[0], "%Y-%m-%d-%H-%M-%S"
        )
    else:
        print(f"Cannot parse timestamp from {basename}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
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

    cur_codes = {
        codemap.get(p.squash_code, p.squash_code)
        for p in data.get_players()
        if p.squash_code
    }

    for known_code, known_player in list(known_players.items()):
        if (
            known_code in cur_codes
            or known_player.player.name in known_players
        ):
            # The player is still registered
            continue

        # The player is no longer registered
        if args.verbose:
            print(f"  Out: {known_player.player!r}", file=sys.stderr)
        del known_players[
            known_code
            if (known_code not in cur_codes)
            else known_player.player.name
        ]
        changecount += 1

    for player in data.get_players():
        code = codemap.get(player.squash_code, player.squash_code)
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
                    if args.verbose:
                        print(
                            f"  Chg: {player!r} ({player.squash_code})",
                            file=sys.stderr,
                        )
                    changecount += 1

            else:
                # The player is new
                if args.verbose:
                    print(
                        f"  New: {player!r} ({code or 'No code'})",
                        file=sys.stderr,
                    )
                known_players[code or player.name] = TimestampPlayer(
                    timestamp, player
                )
                changecount += 1

        elif known_player.player != player:
            s1 = set((known_player.player.data | dict(id=None)).items())
            s2 = set((player.data | dict(id=None)).items())
            diff = [v[0] for v in s2 - s1 if not v[0].startswith("grad")]
            if args.verbose:
                print(
                    f"  Upd: {player!r} ({', '.join(diff)})", file=sys.stderr
                )
            known_players[code] = TimestampPlayer(
                known_player.timestamp, player
            )
            changecount += 1

    if not changecount:
        if args.verbose:
            print(f"  {regfile} adds no new information", file=sys.stderr)
        if args.delete:
            os.remove(regfile)


def key_fn(tsplayer):
    if tsplayer.player.squash_code in args.include:
        return (datetime.datetime(1900, 1, 1), 0)
    else:
        return (tsplayer.timestamp, -tsplayer.player.points)


known_players = sorted(known_players.values(), key=key_fn)

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
    known_players[args.cutoff :], key=lambda p: (p.timestamp, -p.player.points)
)

if players_wl:
    print(f"\n{len(players_wl)} players moved to waiting list:")
    for i, p in enumerate(players_wl):
        print(f"   {i+1:3d}:{p.player} ({p.timestamp})")

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
        special = p.player.squash_code in args.include
        print(f"  {'*' if special else ' '}{cnt:3d}:{p.player}")

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

        players_wl.sort(key=lambda p: -p.player.points)
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
