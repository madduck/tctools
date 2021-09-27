# tctools

This is a collection of tools I've been using to run squash tournaments at [The Thorndon Club](https://thorndonclub.co.nz), working around some of the inflexibilities of [iSquash](https://www.squash.org.nz/sit/grading#/summary), and using [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) to schedule and run the tournaments.

The tools include:

* The [SquashNZ Draw Maker](https://github.com/madduck/tctools/tree/main/draw_maker), a [LibreOffice](https://libreoffice.org) spreadsheet to facilitate making draws;
* A set of [scripts to bulk-process data](https://github.com/madduck/tctools/tree/main/draw_maker), e.g. mail-merging, and exporting email address lists for use in e.g. MailChimp;
* A set of [scripts and templates to publish up-to-date draw and schedule information](https://github.com/madduck/tctools/tree/main/tc2web) from TournamentControl to a web page;
* A [template for draw posters](https://github.com/madduck/tctools/tree/main/poster_maker), automatically generated from TournamentControl data;
* A couple of Linux-specific scripts to [automate data entry into iSquash](https://github.com/madduck/tctools/tree/main/isquash_puppeteer) from TournamentControl export files.

There is a [series of videos to explain how to use
these](https://vimeo.com/user152357033).

Feedback welcome!

## About the TournamentControl export

The [Python](https://python.org) libraries I used to read Excel and
OpenDocument spreadsheets cannot deal with the outdated Excel format exported
by TournamentControl. However, [LibreOffice](https://libreoffice.org), which
is a great Free Software alternative to Microsoft Excel and Google Docs, can.

To use the tools in this repository, you need to open the exported file in
LibreOffice, and save it. There is a `Makefile` to automate this, should you
know what that is.

## Thanks & credits

Kelsey Mackay from KP sent me the draw templates she was using, which gave me
the idea, and informed the design.

Brent Gribbon, also from KP, inspired me with the idea to publish draw and schedule data to a website, and provided his Windows-specific scripts, which I couldn't get working, and rewrote in Python.

Thanks also go to Brad Watts, Nicole Georgel, and the rest of the folks at [The Thorndon Club](https://thorndonclub.co.nz) in Wellington for passing on their knowledge, and coaching me to get up and running quickly. None of what's here would be if it weren't for you, and the opportunity to serve as Squash Club Captain.

## Licence

You are free to use any of the software you find here under the terms of the
[MIT License](https://mit-license.org/), basically meaning that you can do
whatever you want, but you have to attribute copyright, and include a mention
to this licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
