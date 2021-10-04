# SquashNZ Draw Maker

The draw maker is a spreadsheet developed using
[LibreOffice](https://libreoffice.org), which aims to assist in the
pre-tournament phase between collecting registrations on iSquash, and actually
being able to publish your draws. I designed it because I got fed up with
having to deal with changes after I already started colour-coding rows in the
`registrations.xls` file exported from iSquash.

Here are some of the features that might make it interesting to you:

- Simple (albeit manual) import of registrations from iSquash for main event, as well as an (optional) "waiting list" event;

- Data normalisation for players including name and phone number normalisation, both of which are useful for "mail merge" operations;

- Easy interface for assigning players to divisions;

- Method to record playing time restrictions for players, and automatic computation of round 1 & round 2 game days (within limits);

- Tournament time slot planner that allows one to figure out how many people can be hosted, and when games will need to start on any given day;

- Statistics about your players;

- Prize money scratchpad, which auto-calculates the denominations of bills you need to withdraw.

Looking forward to your feedback.

## Installing dependencies

The DrawMaker is a [LibreOffice](https://libreoffice.org) spreadsheet, and uses functionality that is unlikely to be supported by Excel and Google Docs. Please [download and install](https://www.libreoffice.org/get-help/install-howto/) LibreOffice, which is Free Software, to use this tool.

## How to use the Draw Maker

If videos are your thing: I've recorded a [series of
videos](https://vimeo.com/user152357033) to showcase how to use this tool, and
how it facilitates your life.

Here is the gist:

1. For each tournament, please create a copy of the file, rather than editing the master copy, as this may change over time when new functionality is added.

2. Start by "Extracting registrations" from iSquash, which should yield a file `registrations.xls`. Do the same for your waiting list event, if you have one.

3. Open each file in turn, select all cells (`Ctrl-a`), copy all (`Ctrl-c`), then switch to the Draw Maker spreadsheet, select the appropriate of the yellow tabs at the bottom, select all cells here (`Ctrl-a`) and paste the registrations (`Ctrl-v`). Now all registrations are imported.

4. Switch to the Men or the Women tabs. You will see all players from both list in decreasing points order. Waitlisted players are marked red. Now use the first column to assign players to draws. I recommend to start with '0' for the Open, then '1' for Div1, etc..

5. When all players have been assigned, you can verify the result using the "Men's Draws" and "Women's Draws" tabs. You may need to hit `F9` to update the row colours.

6. As players withdraw, or new players jump on the waitlist, or you move players over from the waitlist to the main draws, and re-export the registrations as per the steps above, you will find that the assignments in the "Men" and "Women" tabs will have shifted, and need to be updated. Unfortunately, there is no smart way around this yet.

   1. If all you do is move someone over from the waitlist to the main draw, then everything should be as before — just make sure to remove the line in the "Waiting List" tab, and insert it at the right position in the "Registrations" tab;
   2. As players become unavailable, instead of removing them from the registrations tabs, mark them with an 'X' in the "Men" and "Women" tabs;
   3. If you re-download and re-import from iSquash, you may well have to do some manual work. It's a good idea to make a copy of the file each time you re-import, so that you can refer to how things were before.

7. Player restrictions can be captured on the "Restrictions" tab. The idea here is to put their player code in the first white column, verify that there is a match by checking the name to the left (only works for players in the main draw, not on the waiting list; you can add restrictions for the waitlisted players all the same, you just don't get the name displayed), and then recording the days when a player cannot play. This information will be taken into account when the 1st and 2nd round game days and are computed in the "Men's Draws" and "Women's Draws" tabs, and will also inform the number of games listed for each day in the "Planning" tab.

8. The "Statistics" are automatically computed, but you have to tell the tool which players you consider home players, and which are regional. The way to do this is through the player code, and you may need to expand columns H&I to show the configurables. The format is called [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) and the example listed should give you enough to work with. Just for kicks, if I wanted to consider Levin regional in addition to all the Wellington clubs, I could just use: `WN|CDLV`, or `CD(LV|FN|PN)|WN(TH|IB|CK|MA|TA|KH|WO|HC|UH)`.

9. Finally, the prize money calculator should be straight forward and self-explanatory.

## Screenshots

### Making draws

![image](https://user-images.githubusercontent.com/195073/134892584-56a463b8-e21c-48ed-8ee3-5b3d580bb902.png)

### Planning schedule slots

![image](https://user-images.githubusercontent.com/195073/134892797-3bab0626-c0d0-4323-96b9-52f178e0f71d.png)

### Tournament statistics

![image](https://user-images.githubusercontent.com/195073/134892672-166f47e6-9d8c-44bf-8e8b-7b539dbe0dfd.png)

## Ideas / To-dos:

- Volunteer roster integration;

- A "save-restore" mechanism: provide a view to easily be able to copy-paste player-code-to-draw assignments, such that when a new data set is imported, the previous assignments can be VLOOKUP'd and displayed next to the editable fiels in the draw maker;

## Licence

You are free to use this under the terms of the [MIT
License](https://mit-license.org/), basically meaning that you can do whatever
you want, but you have to attribute copyright, and include a mention to this
licence in whatever you do.

Of course, if you have any improvements, it would be nice if you fed them back
to us.

Copyright © 2021 martin f. krafft <<tctools@pobox.madduck.net>>
