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
# Copyright © 2021–2022 martin f. krafft <m@rtin.kiwi>
# Released under the MIT Licence
#

import argparse
import configparser
import datetime
import jinja2
import pytz
import os
import re
import sys

from pytcnz.dtkapiti.tcexport_reader import TCExportReader
from pytcnz.dtkapiti.game import Game as BaseGame
from pytcnz.warnings import Warnings
from pytcnz.scores import Scores
from pytcnz.util import get_config_filename
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
    def __init__(
        self,
        name,
        player1,
        from1,
        score1,
        player2,
        from2,
        score2,
        status,
        *,
        autoflip_scores=False,
        drawnamepat=r"\w\d{1}",
        **kwargs,
    ):
        try:
            super().__init__(
                name,
                player1,
                from1,
                score1,
                player2,
                from2,
                score2,
                status,
                autoflip_scores=autoflip_scores,
                drawnamepat=drawnamepat,
                **kwargs,
            )
        except Scores.BaseException as e:
            comment = kwargs["comment"]
            del kwargs["comment"]

            msg = f'Unable to parse scores from "{comment}": {e}'
            Warnings.add(msg, context=f"Parsing scores for game {name}")

            super().__init__(
                name,
                player1,
                from1,
                score1,
                player2,
                from2,
                score2,
                Game.Status.error,
                autoflip_scores=autoflip_scores,
                drawnamepat=drawnamepat,
                error=msg,
                **kwargs,
            )

        except Game.InconsistentResultError as e:
            Warnings.add(e, context=f"Reading game {name}")
            super().__init__(
                name,
                player1,
                from1,
                score1,
                player2,
                from2,
                score2,
                Game.Status.error,
                autoflip_scores=autoflip_scores,
                drawnamepat=drawnamepat,
                error=e,
                **kwargs,
            )

    def get_player_class(self, which):
        if self.is_player_known(which):
            if self.get_winner() == self.players[which]:
                return "winner"
            else:
                return ""
        else:
            return "unknown"

    def get_status(self):
        if self.get("error"):
            return "ERROR"

        if self.status == Game.Status.notplayed:
            return "Not played"
        elif self.is_played():
            winner = self.get_winner()
            if not winner:
                return "Awaiting result"
            else:
                ret = f"Won by {winner}"
                if self.scores:
                    ret = f"{ret} in {len(self.scores)}"
                return ret

        elif self.status == Game.Status.on:
            r = f"On {self.court}"
            if self.venue:
                r += f" at {self.venue}"
            return r

        elif self.status == Game.Status.next:
            if self.court:
                return f"Next on {self.court}"
            else:
                # TC actually messes this up, "Soon" without a court is
                # considered "next"
                return "Soon"

        elif self.status == Game.Status.scheduled:
            return ""

        elif self.status == Game.Status.soon:
            ret = "Soon"
            if self.court:
                ret = f"{ret} on {self.court}"
            return ret

        elif self.status == Game.Status.elsewhere:
            return "Awaiting result"

        else:
            return ""

    def get_status_class(self):
        if self.status == Game.Status.next and not self.court:
            # TC actually messes this up, "Soon" without a court is
            # listed as "next"
            return Game.Status.soon.name
        else:
            return self.status.name

    def get_comment(self):
        if error := self.get("error"):
            return error

        elif self.scores:
            s = str(self.scores)
            if len(self.comment) > 0:
                return f"{s} ({self.comment})"
            else:
                return s
        elif self.get_winner():
            return "Scores pending"
        else:
            return self.comment


config = configparser.ConfigParser()
config_filename = get_config_filename()
config.read(config_filename)
draw_name_pattern = config.get(
    "dtkapiti", "draw_name_pattern", fallback=r"\w\d{1}"
)

data = TCExportReader(
    args.spreadsheet,
    Game_class=Game,
    autoflip_scores=True,
    add_games_to_draws=True,
    add_players_to_draws=True,
    add_players_to_games=True,
    drawnamepat=draw_name_pattern,
)
try:
    data.read_all()
except KeyError as e:
    if re.match(draw_name_pattern, str(e).strip("'")):
        print(f"Could not find draw {e}, maybe you need to set "
              f"'draw_name_pattern' in {config_filename} …?")
        sys.exit(os.EX_CONFIG)
    else:
        raise

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
