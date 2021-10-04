# tc2web

This is a set of simple templates and scripts that take data from
[TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) by way of their
on-save export function (has to be enabled in settings) and create
mobile-friendly HTML pages for draws, as well as the schedule.

See https://thorndonclub.co.nz/tc/ for an example.

As TournamentViewer is only available for Android, this provides a nice
cross-platform way for people to keep up-to-date on a tournament without
having to install software that may not be available for their phone.

The included `upload.sh` file takes care of simply pushing the resulting files
to an FTP server. It expects a file `upload.creds` with the access data:

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

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
