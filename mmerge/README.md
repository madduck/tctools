# TC "mail"-merge script

This is a [Python](https://python.org) script that makes
use of [PyExcel](http://www.pyexcel.org/) to give access to the data in the [DrawMaker](https://github.com/madduck/tctools/tree/main/draw_maker), as well
as [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) exports.

## Usage

```
# send a message to all players in all draws:
./player_mmerge.py draw_maker.ods 'sms {number} Kia ora {first name}, welcome to the {tournament}!'

# send a message to people on the waiting list:
./player_mmerge.py draw_maker.ods -w 'sms {number} Sorry we cannot host you, {first name}!'

# list all male player codes in B grade:
./player_mmerge.py -g m -p 2700-3499 tc-export-fixed.xls '{grading code}'

# generate a HTML page to record fees paid
./player_mmerge.py tc-export-fixed.xls -t entry_fees_sheet.j2 > sheet.html
```

Note that to use a TC exported spreadsheet, it needs to be fixed by loading and saving it with LibreOffce, since PyExcel cannot read the ancient format TC writes. There is a script [fix-tc-export.sh](https://github.com/madduck/tctools/blob/main/fix-tc-export.sh) that does this.

Have a look at how I [send bulk SMS](https://github.com/madduck/tctools/blob/main/mmerge/README.SMS.md), which is an essential ability for running successful tournaments.

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
