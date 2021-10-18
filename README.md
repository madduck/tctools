# tctools

This is a collection of tools I've been using to run squash tournaments at [The
Thorndon Club](https://thorndonclub.co.nz) for [Squash New
Zealand](https://www.squashnz.co.nz), working around some of the peculiarities
of [iSquash](https://www.squash.org.nz/sit/grading#/summary), and using
[TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) to schedule and
run the tournaments. The use of TournamentControl is optional, but highly recommended. Other tournament software may be integrated into these tools in the future.

The tools include:

* The [SquashNZ DrawMaker](https://github.com/madduck/tctools/tree/main/draw_maker), a [LibreOffice](https://libreoffice.org) spreadsheet to facilitate making draws;
* A set of [scripts to bulk-process data](https://github.com/madduck/tctools/tree/main/scripts), e.g.
  * mail-merging, and exporting email address lists for use in e.g. MailChimp;
  * automatically making and seeding draws in iSquash after creating them in DrawMaker;
  * searching the grading list, and bulk-registering players to waiting lists, so as to use them in the DrawMaker;
  * automated entering of game scores for tournaments into iSquash.
* A set of [scripts and templates to publish up-to-date draw and schedule information](https://github.com/madduck/tctools/tree/main/tc2web) from TournamentControl to a web page;
* A [template for draw posters](https://github.com/madduck/tctools/tree/main/poster_maker), automatically generated from TournamentControl data;

There is a [series of videos to explain how to use
these](https://vimeo.com/user152357033).

[Feedback welcome](mailto:tctools@pobox.madduck.net)!

I am not affiliated with Squash New Zealand. Fair use of their infrastructure is claimed. If you (ab)use these tools for any other purpose than squash tournament control, you may be held liable, as access *is* logged.

## Downloading `tctools`

There are two ways in which you can download `tctools` to your computer, or the one used for a tournament: downloading a Zip file, or using special software to track development of the tools.

### A Zip-file for every tournament (simple/beginner)

The **generally recommended way is to [download a Zip file](https://github.com/madduck/tctools/archive/refs/heads/main.zip)** for every tournament, which you then unpack wherever you want it to live, and never worry about again post-tournament. In the event of bug fixes, you can either directly replace the affected files, or just re-download as required.

### Using a version control system (harder/advanced)

On the other hand, and especially if you are keen on contributing and helping making the tools better, please consider to use [Git for Windows](https://git-scm.com/download/win), which allows you to easily update as changes are made upstream, and also submit your changes and improvements back upstream.

Downloading Git and installing it might seem scary at first, as there are a lot of questions asked. However, you are fine just accepting the defaults for everything. Then, once installed, use the command line / PowerShell and enter:

```
git clone https://github.com/madduck/tctools.git
```

and you will find `tctools` in the subdirectory `tctools`. Easy as.

To update, change to that directory and run `git pull` to upgrade the local copy to the latest version. Git is very cool, and here's [starter article to read](https://guides.github.com/introduction/git-handbook/) in case you're keen to learn.

## Installing dependencies

### LibreOffice

The DrawMaker is written using [LibreOffice](https://libreoffice.org), which
you will need to
[install](https://www.libreoffice.org/get-help/install-howto/), as it uses
functionality not available in Excel or Google Docs. You also need LibreOffice
in combination with TournamentControl, as detailed in the next section:

### Python and pytcnz

If you want to use the [scripts](https://github.com/madduck/tctools/tree/main/scripts) or [tc2web](https://github.com/madduck/tctools/tree/main/tc2web) — and trust me, you do, unless you want to make and seed draws manually, or enter results by hand – you will need to install [Python](https://python.org), as [detailed here](https://www.python.org/downloads/).

Once installed, you need to obtain the [pytcnz](https://github.com/madduck/pytcnz) library, which used to be part of `tctools`, but has been split off into a separate library.

Once Python is installed, the `pytcnz` library, as well as all dependencies can be installed with a single command (you might need to install `pip` first, if the following gives an error).

```
pip install git+https://github.com/madduck/pytcnz@main
python -m pytcnz.welcome
```

This is also the command to run to upgrade the library.

If you saw my little message, you should be good to go, e.g.

```
python scripts\search_grading_list --name martin --club WNTH --grade b
```

### Gecko web driver

To remote-control iSquash, you need to install [geckodriver](https://github.com/mozilla/geckodriver). Grab the [latest release](https://github.com/mozilla/geckodriver/releases/latest) ([`geckodriver-v0.30.0-win64.zip`](https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-win64.zip) at time of writing), open the Zip file, and copy the contained `geckodriver.exe` file into the `scripts` subdirectory of `tctools`, or anywhere else where the operating system can find it (your "`$PATH`").

Please note that if you install `geckodriver` to the scripts directory, you can only run the scripts controlling iSquash from within that directory.

### About the TournamentControl export

The [Python](https://python.org) libraries I use to read Excel and
OpenDocument spreadsheets cannot deal with the outdated Excel format exported
by TournamentControl. However, [LibreOffice](https://libreoffice.org), which
is a great Free Software alternative to Microsoft Excel and Google Docs, can.

To use the tools in this repository, you need to open the exported file in
LibreOffice, and save it.

There is a script
[fix-tc-export.sh](https://github.com/madduck/tctools/blob/main/fix-tc-export.sh)
that does this.

## Thanks & credits

Kelsey Mackay from KP sent me the draw templates she was using, which gave me
the idea for the [poster-maker](https://github.com/madduck/tctools/tree/main/poster_maker), and informed the design.

Brent Gribbon, also from KP, inspired me with the idea to publish draw and schedule data to a website, and provided his Windows-specific scripts, which I couldn't get working, and rewrote in Python. It was all downhill from there.

Thanks also go to Brad Watts, Nicole Georgel, and the rest of the folks at [The Thorndon Club](https://thorndonclub.co.nz) in Wellington for passing on their knowledge, and coaching me to get up and running quickly. None of what's here would be if it weren't for you, and the opportunity to serve as Squash Club Captain.

## Licence

You are free to use any of the software you find here under the terms of the
[MIT License](https://mit-license.org/), basically meaning that you can do
whatever you want, but you have to attribute copyright, and include a mention
to this licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
