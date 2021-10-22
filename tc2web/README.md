# tc2web

This is a set of simple templates and scripts that take data from
[TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) by way of their
on-save export function (has to be enabled in settings) and create
mobile-friendly HTML pages for draws, as well as the schedule.

See https://thorndonclub.co.nz/tc/ for an example.

As TournamentViewer is only available for Android, this provides a nice
cross-platform way for people to keep up-to-date on a tournament without
having to install software that may not be available for their phone.

## Installing dependencies

For this to work, you need to install:

* Python 3.9 or later, as well as `pytcnz`. Please refer to [the section in tctools' README file](https://github.com/madduck/tctools#python-and-pytcnz) on how to install those;
* The `python-jinja2` templating library, which you can install from the Windows PowerShell like so: `pip install Jinja2`;
* [NcFTP](https://www.ncftp.com/download/) to handle the FTP upload.

## Uploading

The included `upload.sh` file takes care of simply pushing the resulting files
to an FTP server, and you need to install [NcFTP](https://www.ncftp.com/download/) for that to work. The script expects a file `upload.creds` with the access data:

```
FTPUSER=username
FTPPASS=password
FTPHOST=ftp.example.org
TARGETDIR=/tc/
```

Which FTP server to use, and what URL can then be used to access the uploaded files is unfortunately something you have to figure out yourself.

## Exporting from TournamentControl

For once-off exports, use the menu on the main screen:

![Screenshot](https://user-images.githubusercontent.com/195073/135780105-c88bf3be-5280-4ac8-ab62-4d1eefb7cd36.png)

## Running with TournamentControl

As you are running a tournament, you will want to be running this code on the same PC as is used to control the tournament, i.e. the one running TournamentControl. The files to make that happen are included in the `windows` subdirectory, and more information is available in the [the README file](https://github.com/madduck/tctools/blob/main/tc2web/windows/README.md) file.

## Entering scores during the tournament

`tc2web` needs you to enter match results into the game comments in TournamentControl to be able to parse and display them. This can be done either before or after telling TournamentControl who won the game, and thus moving the game up to the "Marking" row. It's good practice to maintain the player order, i.e. record "4-11 5-11 10-12" if player 2 won. The tools will attempt to automatically flip the scores if entered wrongly, but it's best if they don't have to be smart.

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
