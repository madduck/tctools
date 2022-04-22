# tc2web on Windows

To allow the data from TournamentControl to make its way to the website at regular intervals, you need to install a couple of prerequisites on the TC computer, and also configure [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) to auto-export the data when you've made changes.

## Installing pre-requisites

The following software packages must be installed:

* [LibreOffice](https://www.libreoffice.org/), at least while there is no other way to fix the exported data file;
* [Python 3.9](https://www.python.org/) or newer;
* [MiniCap](https://www.donationcoder.com/software/mouser/popular-apps/minicap) for the screenshotting;
* [NcFTP](https://www.ncftp.com/) to handle the uploading.

Once Python is installed, you also need to pull a couple of libraries with the following command run from the command prompt / PowerShell:

```
pip install jinja2 xlrd pytz
```

## Configuring TournamentControl to auto-export

The settings are accessible from the top right of the TournamentControl screen:

![Screenshot](https://user-images.githubusercontent.com/195073/135780176-5cc9383c-b653-4e59-8536-1c0bb7677c5c.png)

Then at the bottom of the settings, you will find the auto-export function:

![Screenshot](https://user-images.githubusercontent.com/195073/135780204-afbf46f2-c8de-47ee-9889-2dd108abfc09.png)

For file location, please make sure that you have selected the top directory of the   `tctools`, and chosen `tc-export.xls` as the filename.

It is also advisable to configure auto-save in the settings, so that the file is      exported if the machine is left idle, otherwise changes are only propagated if you hit "save" explicitly.

![Screenshot](https://user-images.githubusercontent.com/195073/135780292-fd8a2b8f-1e8e-4071-9fda-b5edd88df970.png)

## Running the update loop

The main script `bgupdater.bat` is designed to run in the background and will loop indefinitely, which is fine even if TournamentControl is not running. Therefore, it might be a good idea to start it automatically on the TC computer:

1. Create a shortcut to the `bgupdater.bat` (using the right-click context menu in the Explorer);
2. Modify its properties (also right-click), and change "Run: Normal Window" to "Run: Minimized".
3. Select it, and hit `Ctrl-c`;
2. Hit `Windows-R` and type `shell:startup` into the dialog;
3. Hit `Ctrl-v` and the file should appear in the new destination. Overwrite or remove any previous shortcuts;
4. Reboot and verify that there now a minimised command line window in the task bar:

![image](https://user-images.githubusercontent.com/195073/135781870-2bab72e3-1709-44d4-9b6d-1e42da2208c5.png)

Now you are ready to roll!

## Licence

You are free to use any of the software you find here under the terms of the
[MIT License](https://mit-license.org/), basically meaning that you can do
whatever you want, but you have to attribute copyright, and include a mention
to this licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021–2022 martin f. krafft <<tctools@pobox.madduck.net>>
