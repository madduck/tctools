#!/usr/bin/python3
#
# Extract games schedule and draws from a TournamentControl
# export spreadsheet, and turn them into a simple HTML view
#
# Expects the score to be entered for finished games in the
# form of 4-11 11-3 11-2 11-6 where the first number always
# refers to the player named first, and the second to the
# player named second.
#
# Copyright © 2021 martin f. krafft <m@rtin.kiwi>
# Released under the MIT Licence
#

import argparse
import datetime
import pytz
import os
import jinja2

from pytcnz.dtkapiti.tcexport_reader import TCExportReader
from pytcnz.dtkapiti.game import Game as BaseGame
import pytcnz.meta as META

parser = argparse.ArgumentParser(
    description="Collect games & draws info and fill a template"
)

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
    "--template",
    "-t",
    metavar="TEMPLATE_FILE",
    type=str,
    required=True,
    help="Jinja2 template to use",
)
parser.add_argument(
    "--output",
    "-o",
    metavar="OUTPUT_FILE",
    type=str,
    required=True,
    help="File to write",
)
args = parser.parse_args()


class Game(BaseGame):
    def get_player_class(self, which):
        if self.is_player_known(which):
            if self.get_winner() == self.players[which]:
                return "winner"
        else:
            return "unknown"

    def get_status(self):
        if self.status == Game.Status.notplayed:
            return "Not played"
        elif self.status <= Game.Status.justfinished:
            winner = self.get_winner()
            if not winner:
                return "Awaiting result"
            else:
                return f"Won by {winner} in {len(self.scores)}"

        elif self.status == Game.Status.on:
            r = f"On {self.court}"
            if self.venue:
                r += f" at {self.venue}"
            return r

        elif self.status == Game.Status.next:
            return f"Next on {self.court}"

        elif self.status == Game.Status.scheduled:
            return ""

        elif self.status == Game.Status.soon:
            return "Soon"

        else:
            self.status = ""

    def get_status_class(self):
        return self.status.name

    def get_comment(self):
        if self.scores:
            s = str(self.scores)
            if len(self.comment) > 0:
                return f"{s} ({self.comment})"
            else:
                return s
        else:
            return self.comment


data = TCExportReader(
    args.spreadsheet,
    Game_class=Game,
    autoflip_scores=True,
    add_games_to_draws=True,
    add_players_to_draws=True,
    add_players_to_games=True,
)
data.read_all()

timestamp = datetime.datetime.now(
    tz=pytz.timezone("Pacific/Auckland")
).strftime("%F %T %Z")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.getcwd()),
    autoescape=jinja2.select_autoescape(["j2"]),
)
template = env.get_template(args.template)
with open(args.output, "w") as f:
    print(
        template.render(
            meta=META,
            timestamp=timestamp,
            tournament_name=data.get_tournament_name(),
            draws=data.get_draws(),
            players=data.players,
            pending_games=data.get_pending_games(),
            played_games=data.get_played_games(),
        ),
        file=f,
    )
