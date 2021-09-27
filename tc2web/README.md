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

## Screenshotting TournamentControl

There is a component missing that I will import soon, which is intended to be
run on the Windows PC at the tournament, to screenshot the display and push an
image every couple of minutes for people to remote-view court allocations.

I've thought about recreating the display in HTML, but there is currently no
way to get updated information from TournamentControl other than when data are
being saved, and that only happens irregularly, so wouldn't be of much use for
information that changes before and after each game on every court. Hopefully,
the guys from TournamentControl will provide us with an API to access the live
data at some point.

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
