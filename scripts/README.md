# TC scripts

This directory contains scripts that facilitate aspects of squash tournament
control. Most of these are written in [Python](https://python.org), and make use of the [pytcnz](https://github.com/madduck/pytcnz) library, except for the ones whose names end in `.sh` — these are simple shell scripts that just call the Python scripts in specific ways.

## Prerequisites

To run most of these, you need:

* [Python](https://python.org) 3.9 or newer;
* [pytcnz](https://github.com/madduck/pytcnz) and related libraries, which can be installed like this: `pip install git+https://github.com/madduck/pytcnz@main`

## The scripts

All Python scripts can be invoked with `--help` to get information on the arguments and parameters they take.

### Searching the grading list

If you're not keen on using the Web interface for grading list searches, you can use this script to do so from the command line:

```PowerShell
> python ./search_grading_list.py --name Martin --grade B --club WNTH
WNTHMK	Martin Krafft	M	B2	2790	The Thorndon Club
```

### Bulk-registering players

Given a set of search criteria, register players for a tournament in bulk. This is mainly useful when you need to fill in a hole in the draws, and you do not have matching players on your waiting list. In this case, running e.g.

```PowerShell
> python ./bulk_register_players.py -u username -p password -t TOURNAMENTCODE \
    --district WN --gender f --min 1250 --max 1420
```

will go to the grading list, get a list of all female players in that points range who are registered to play in Wellington and register them on the iSquash event specified with `TOURNAMENTCODE`. Once done, you can then extract the registrations file anew, and contact the individual players to see if they can fill in.

### Player "mail-merge"

This tool constructs lines of text with player data, similar to how "mail-merge" functionality might fill in a mail letter template. What you then do with these lines is up to you. Have a look at how I [send bulk text messages](https://github.com/madduck/tctools/blob/main/mmerge/HOWTO-SMS.md) for inspiration.

```
## send a message to all players in all draws:
> python ./player_mmerge.py --drawmaker draw_maker.ods \
    'sms {number} Kia ora {first name}, welcome to the {tournament}!'

## send a message to people on the waiting list:
> python ./player_mmerge.py --drawmaker draw_maker.ods --all --waitlist \
    'sms {number} Sorry we cannot host you, {first name}!'

## send a message to waitlisted people in the draws:
> python ./player_mmerge.py --drawmaker draw_maker.ods --waitlist \
    'sms {number} {first name}, still keen?'

## list all male player codes in B grade:
> python ./player_mmerge.py --gender m --points 2700-3499 \
    --tcexport tc-export-fixed.xls '{grading code}'

## generate a HTML page to record fees paid (see make_entry_fees_sheet.sh)
> python ./player_mmerge.py --tcexport tc-export-fixed.xls \
    --template entry_fees_sheet.j2 > sheet.html
```

#### Mailchimp import

The `mailchimp_import.sh` script invokes the mail-merge tool to create data that one can copy-paste into the audience import function of Mailchimp, to register players, and also tag them accordingly. You need the `xclip` utility installed, or just modify the script to print to the console, so you can copy it from there.

```
# Tag all players in the draws with the tag 2021-10-open,
# as well as all waitlisted players with 2021-10-open-wl
> ./mailchimp_import.sh ../draw_maker.ods 2021-10-open
```

#### Make a sheet to record entry fees

To create a table allowing your bar staff to record who has paid entry fees, use the `make_entry_fees_sheet.sh` script (or just run the command therein by hand):

```PowerShell
> ./make_entry_fees_sheet.sh ../tc-export-fixed.xls
```

This will open the browser from where you can print the sheet.

### Managing iSquash tournaments

This tool provides 4 modes of operation, which we'll introduce in turn:

#### Registering players

To ensure that all players assigned to draws in the DrawMaker are also registered to the tournament on iSquash, run:

```PowerShell
> python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
>   -i ../draw_maker.ods regs --register
```

You can also specify `--update` to update the player comments for all players, in case you have made changes to those in the draw maker.

#### Clearing all registrations

If, for whatever reason, you'd like to clear all registrations of an event on iSquash, run this:

```PowerShell
> python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
>   -i ../draw_maker.ods regs --clear
```

#### Making and seeding draws

To create a draw on iSquash for every draw you've created in the DrawMaker, run the tool as follows:

```PowerShell
> python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
>   -i ../draw_maker.ods draws --make
```

Optionally, also specify:

* `--delete` to first delete each draw, i.e. remaking it (for when there are structural changes);
* `--seed` to seed it with the assigned players, and initialise all matches;
* `--update-web` to update the Web diagram at the end of the run
* `--draw CODE` for each draw to which you want to limit this run, i.e. if you only want the above to happen for the Women's Open and Div 1 draws, specify `-d W0 -d W1`;
* `--draw-type` if you want to override the default draw type chosen, e.g. if you want a type C 6 draw instead of the type B default for the Men's Div 6: `--draw-type M6=6c` (specify once for each draw);
* `--draw-desc` if you don't like the default names given to the draws, e.g. `--draw-desc M4="Mens 4th Division"` (specified once for each draw);
* `--register-players` to register any players not yet registered prior to seeding the draws.

#### Deleting draws

To delete draws, use as follows:

```PowerShell
> python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
>   -i ../draw_maker.ods draws --delete
```

and optionally specify which draws to delete using the `--draw`/`-d-` arguments, as above.

### Entering scores into iSquash

As soon as the first game scores have been entered into the comment field of played games using TournamentControl, you can fire off this script to start entering the results. It will do as much as it can, and then just exit and wait for you to run it again, and again… or just run it at the very end.

**Warning**: the script does not change the game status to "Not Played" for byes, so this has to be done manually, although you can record those games as "11-0 11-0 11-0" for the time being.

```PowerShell
> python ./enter_isquash_results.py -u username -p password -t TOURNAMENTCODE \
>   -i ../tc-export-fixed.xls
```

You can use `-d`/`--draw` any number of times to limit processing to the given
draws.

If you specify `--reset`, then all game scores are reset to 0.

Finally, pass `--publish`, and the scores will be submitted to the grading list once entered. Use `-d -` to skip entry, e.g. if you just want to publish.

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
