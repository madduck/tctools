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

I've recorded a [series of videos](https://vimeo.com/user152357033) to
showcase how to use this tool, and how it facilitates your life.

Looking forward to your feedback.

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
