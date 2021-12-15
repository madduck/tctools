# Generating score sheets

`tctools` can use the data exported by [TournamentControl](https://tournamentcontrol.dtkapiti.co.nz/) to generate scoresheets that are filled in with individual match data, such as the player names, game code, and time. This is done by making use of the "mail-merge" functionality of [LibreOffice](https://libreoffice.org), which you will need to [download and install](https://www.libreoffice.org/get-help/install-howto/). LibreOffice is Free Software.

Setup can be a bit finnicky, so please make sure you follow the steps in the exact order as outlined:

1. Make a copy of the `scoresheet.ods` file and place it into the same directory as the `tc-export-fixed.xls` file. If you do not have that file but `tc-export.xls`, make sure you run [`fix-tc-export.sh`](https://github.com/madduck/tctools/blob/main/fix-tc-export.sh), or just make a copy of the file, and name it `tc-export-fixed.xls`. Do not open the scoresheet without this file;

2. Now open the file and verify that the mail-merge toolbar is visible, and hit the "Next" key, and the data from the first game should appear in the fields of the scoresheet;

![image](https://user-images.githubusercontent.com/195073/146183051-9edc9a72-3c8d-42de-9d2a-7016c39d7027.png)

3. By using the Data Sources button (1), you can get access to the games data;

![image](https://user-images.githubusercontent.com/195073/146183856-58e7da61-0018-4d14-bb59-d86fe2533fd9.png)

4. It is a good idea to use the Sort button (2) to sort the games by the "Day/time" field and print in that order so that the next games will always be on top of the stack;

5. Use the Filter button (3) to limit the set of files to print at any point in time to e.g. "Day/time is like 'Thu*'" to only print Thursday's sheets. Then print Friday's sheets when the Thursday data has been exported.

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
