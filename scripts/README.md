# TC scripts

This directory contains scripts that facilitate aspects of squash tournament
control. Most of these are written in [Python](https://python.org), and make use of the [pytcnz](https://github.com/madduck/pytcnz) library, except for the ones whose names end in `.sh` — these are simple shell scripts that just call the Python scripts in specific ways, and getting them to run on Windows is definitely beyond the scope of this document.

## Prerequisites

To run most of these, you need:

* [Python](https://python.org) 3.9 or newer;
* [pytcnz](https://github.com/madduck/pytcnz) and related libraries, which can be installed like this: `pip install git+https://github.com/madduck/pytcnz@main`

## The scripts

All Python scripts can be invoked with `--help` to get information on the arguments and parameters they take.

Those scripts interacting with iSquash either need the user credentials and tournament code passed on the command line, or you may create a file `tctools.ini` in the tournament's root directory, and provide the details there. Please have a look at the [`tctools.ini.example`](https://github.com/madduck/tctools/blob/main/tctools.ini.example) file.

### Searching the grading list

If you're not keen on using the Web interface for grading list searches, you can use this script to do so from the command line:

```shell
⌨ python ./search_grading_list.py --name Martin --grade B --club WNTH
WNTHMK	Martin Krafft	M	B2	2790	The Thorndon Club
```

### Bulk-registering players

Given a set of search criteria, register players for a tournament in bulk. This is mainly useful when you need to fill in a hole in the draws, and you do not have matching players on your waiting list. In this case, running e.g.

```shell
⌨ python ./bulk_register_players.py -u username -p password -t TOURNAMENTCODE \
    --district WN --gender f --min 1250 --max 1420
```

will go to the grading list, get a list of all female players in that points range who are registered to play in Wellington and register them on the iSquash event specified with `TOURNAMENTCODE`. Once done, you can then extract the registrations file anew, and contact the individual players to see if they can fill in.

### Player "mail-merge"

This tool constructs lines of text with player data, similar to how "mail-merge" functionality might fill in a mail letter template. What you then do with these lines is up to you. Have a look at how I [send bulk text messages](https://github.com/madduck/tctools/blob/main/mmerge/HOWTO-SMS.md) for inspiration.

```shell
## send a message to all players in all draws:
⌨ python ./player_mmerge.py --drawmaker draw_maker.ods \
    'sms {number} Kia ora {first name}, welcome to the {tournament}!'

## send a message to people on the waiting list:
⌨ python ./player_mmerge.py --drawmaker draw_maker.ods --all --waitlist \
    'sms {number} Sorry we cannot host you, {first name}!'

## send a message to waitlisted people in the draws:
⌨ python ./player_mmerge.py --drawmaker draw_maker.ods --waitlist \
    'sms {number} {first name}, still keen?'

## list all male player codes in B grade:
⌨ python ./player_mmerge.py --gender m --points 2700-3499 \
    --tcexport tc-export-fixed.xls '{grading code}'

## generate a HTML page to record fees paid (see make_entry_fees_sheet.sh)
⌨ python ./player_mmerge.py --tcexport tc-export-fixed.xls \
    --template entry_fees_sheet.j2 > sheet.html
```

#### Mailchimp import

The `mailchimp_import.sh` script invokes the mail-merge tool to create data that one can copy-paste into the audience import function of Mailchimp, to register players, and also tag them accordingly. You need the `xclip` utility installed, or just modify the script to print to the console, so you can copy it from there.

```shell
# Tag all players in the draws with the tag 2021-10-open,
# as well as all waitlisted players with 2021-10-open-wl
⌨ ./mailchimp_import.sh ../draw_maker.ods 2021-10-open
```

#### Make a sheet to record entry fees

To create a table allowing your bar staff to record who has paid entry fees, use the `make_entry_fees_sheet.sh` script (or just run the command therein by hand):

```shell
⌨ ./make_entry_fees_sheet.sh ../tc-export-fixed.xls
```

This will open the browser from where you can print the sheet.

### Managing iSquash tournaments

The `manage_isquash_tournament.py` script takes care of all your pre-tournament and tournament management/design needs. It exposes pretty much all of the functionality of iSquash's tournament module for the pre-tournament phase. To get your bearing, call it with `--help`:

```
⌨ python ./manage_isquash_tournament.py --help
usage: manage_isquash_tournament.py [-h] --username USERNAME --password PASSWORD
                                    --tournament TOURNAMENT_CODE [--debug]
                                    [--headless] --input DRAWMAKER_FILE [--register]
                                    [--update] [--seed]
                                    [--extract-registrations REGISTRATIONS_FILE]
                                    [--delete] [--make] [--draw-type DRAW=TYPE]
                                    [--draw-desc DRAW=DESC] [--populate]
                                    [--extract-draws DRAWS_FILE] [--update-web]
                                    [--draw DRAW_CODE]

Manage tournaments on iSquash

optional arguments:
  -h, --help            show this help message and exit

iSquash interaction:
  Data required to interact with iSquash

  --username USERNAME, -u USERNAME
                        iSquash user name for login
  --password PASSWORD, -p PASSWORD
                        iSquash password for login
  --tournament TOURNAMENT_CODE, -t TOURNAMENT_CODE
                        iSquash tournament code

Runtime control:
  --debug               Drop into debugger on error
  --headless            Operate without a browser window (invisible)

Input:
  --input DRAWMAKER_FILE, -i DRAWMAKER_FILE
                        DrawMaker file to read

Operations:
  The main operations relating to managing tournaments on iSquash. All of these
  can be combined, or run individually, as needed.

  --register            Ensure all players are registered for the draws being
                        processed
  --seed                Adjust the grading list points for ALL players. It is not
                        possible to do this just for a subset, or per-draw. Use with
                        care. If you need to override grading points for a player,
                        you will need to do this manually for now.
  --extract-registrations REGISTRATIONS_FILE
                        Extract registrations file when done
  --delete              Delete draw or draws. Run this before making them if there
                        were structural changes. Draws with results entered already
                        cannot be deleted.
  --make                Make draws that do not exist yet, or which have been
                        deleted.
  --populate            Populate draws with players. This will also initialise the
                        matches.
  --extract-draws DRAWS_FILE
                        Extract draws file when done.
  --update-web          Update Web diagram when done

Registering players:
  These options only make sense in the presence of --register

  --update              Update player comments for registered players

Making draws:
  These options only make sense in the presence of --make

  --draw-type DRAW=TYPE, -y DRAW=TYPE
                        Specify types for draws, e.g. M4=6b; Choices: 8, 16, 16no34,
                        32, 4rr, 5rr, 6rr, 6b, 6c, 16swiss
  --draw-desc DRAW=DESC, -n DRAW=DESC
                        Override long descriptions for draws, e.g. M4="Mens 4th
                        Division"

Limiting:
  Use these options to limit operations

  --draw DRAW_CODE, -d DRAW_CODE
                        Only operate on the given draw, or draws if specified more
                        than once
```

Typically, you'd use the tool once you've assigned players to draws in the DrawMaker spreadsheet, and invoke it like this:

```shell
⌨ python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
    --input ../draw_maker.ods \
    --register --update \
    --extract-registrations ../TIMESTAMP-registrations.xls \
    --make --populate \
    --extract-draws ../TIMESTAMP-draws.xls \
    --update-web
```

and then go and grab a coffee or beverage of choice while it works its magic. Invoked like this, the tool will:

1. Ensure that all players assigned to draws are registered to the event on iSquash, and register those that aren't yet (`--register`). It'll also update the comments of all registered players with what you have in the DrawMaker (`--update`). If you have not made any changes to the player comments, you do not need this, and it'll save a minute or two of runtime not to include this flag.

2. Once all players are registered, the tool will extract the registrations spreadsheet to `../TIMESTAMP-registrations.xls`; `TIMESTAMP` will be replaced by the current date and time, if part of the name. This is optional.

3. Make all draws (which don't exist yet) (`--make`), populate them with the assigned players, and initialise the matches (`--populate`). This will overwrite previous seedings as required, and is idempotent in that it can be run again and again. If you made structural changes to the draws and e.g. split an 8-draw into two 4-draws, you will need to specify `--delete` to remove the draws prior to remaking them.

4. Extract the draws to `../TIMESTAMP-draws.xls`. As before, if the filename includes `TIMESTAMP`, it will be replaced by the current date and time, which is optional.

5. Finally, the tool will update the Web diagram on iSquash.

When making draws, the tool tries to induce the draw type from the number of players, and will assume sensible defaults, e.g. a 6 Type B draw when there are 6 players. You can override this heuristic by appending e.g. `--draw-type M6=6c`, which will make the M6 draw a 6 Type C draw. See the `--help` output for the available choices.

Draw names/descriptions are also automatically generated form the draw code, and can be overridden by appending e.g. `--draw-desc M4="Mens 4th Division"` for each draw you'd like to name differently.

Finally, if you know that you only need to work on a subset of draws, chuck a filter at the end of the command: `--draw M2 --draw M3` will make the script only work on those two draws, and leave the others untouched. Note, however, that if you specify `--seed` to update the player seedings, this will happen for *all registered players*.

#### Snapshotting registrations

Another use-case of `manage_isquash_tournament.py` is to snapshot registrations at regular intervals:

```shell
⌨ python ./manage_isquash_tournament.py -u username -p password -t TOURNAMENTCODE \
    --extract-registrations ../TIMESTAMP-registrations.xls --headless
```

Note the use of the `--headless` option, which will essentially just run this without even showing you the browser window, so it won't disturb your workflow.

Run regularly, this will create a series of files, which can later be used to identify the first `n` players that have signed up, i.e. when you need to make a call whom to exclude from the tournament because you have too many players. Check out the `split_off_waitinglist.py` tool, which does just that.

### Splitting off a waiting list

If you do not have a separate waiting list event for your tournament, you will possibly end up with too many registrations, and no easy way to determine whom to slash, other than cutting at the low end of points, but that's not how squash in New Zealand works. Unfortunately, iSquash does not record the date and time when a player registers, so you have to make do:

1. Run the `./manage_isquash_tournament.py` tool to [extract registrations at regular intervals and with the `TIMESTAMP` placeholder in the filename](#snapshotting-registrations);

2. Use `split_off_waitinglist.py` to select the `N` players who registered before the others, and move everyone else to a waiting list:

```shell
⌨ python ./split_off_waitinglist.py -o ../registrations.ods -c 64 \
    ../*-registrations.xls
```

Note how the last argument includes an asterisk, causing it to consider all files matching that pattern in the parent directory.

This will create a new file `../registrations.ods` with two tabs; The first 64 players who have registered are on the first tab, and the rest on the second tab. Should you prefer two separate files, you can pass `-w ../waitlist.ods` as well to have the waitlisted players moved there.

If you want to write an Excel file, e.g. `registrations.xls`, you need to install the `xlwt` library: `pip install xlwt`.

For the logic to work, you must use the `TIMESTAMP` placeholder in the file name when extracting registrations, and the accuracy depends on how often you've extracted snapshots of the registrations.

If the limit is reached between two snapshots, then higher-graded players are given precedence over lower-graded players.

Finally, if you add `--verbose` (or `-v`) to the command line, you'll get shown a lot of information about how registrations change between two snapshots.

#### Convenience wrapper

For Linux users, `snapshot_registrations.sh` is a convenience script which:

1. Headlessly downloads current registrations;

2. Removes the file if there have not been any changes;

3. Runs `split_off_waitinglist.py` against all files in the `snapshots` directory.

The tool takes the cut-off count as first argument, and optionally an output filename, or it will skip writing a file.

### Resetting a tournament

Should you, for whatever reason, want to reset a tournament, you can do so using `reset_isquash_tournament.py`:

```shell
## Delete all draws
⌨ python ./reset_isquash_tournament.py -u username -p password -t TOURNAMENT_CODE \
    --draws

## Also unregister all players:
⌨ python ./reset_isquash_tournament.py -u username -p password -t TOURNAMENT_CODE \
    --draws --players

## Unregister all players not assigned to draws:
⌨ python ./reset_isquash_tournament.py -u username -p password -t TOURNAMENT_CODE \
    --players
```

### Entering scores into iSquash

As soon as the first game scores have been entered into the comment field of played games using TournamentControl, you can fire off this script to start entering the results. It will do as much as it can, and then just exit and wait for you to run it again, and again… or just run it at the very end.

**Heads-up!** For this to work, you must enter the results of played games into the comments field of played games. This can be done either before or after telling TournamentControl who won the game, and thus moving the game up to the "Marking" row. It's good practice to maintain the player order, i.e. record "4-11 5-11 10-12" if player 2 won. The tools will attempt to automatically flip the scores if entered wrongly, but it's best if they don't have to be smart.

**Warning**: the script does not change the game status to "Not Played" for byes, so this has to be done manually, although you can record those games as "11-0 11-0 11-0" for the time being.

```shell
⌨ python ./enter_isquash_results.py -u username -p password -t TOURNAMENTCODE \
    -i ../tc-export-fixed.xls
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
