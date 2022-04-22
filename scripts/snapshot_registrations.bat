:: snapshot_registrations.bat — snapshot registrations
::
:: Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence

@echo off
setlocal

cd /d %~dp0"

set "SNAPSHOTDIR=..\snapshots"

if [%~2]==[] goto doit

set "OUTOPT=--output %2"

:doit
python manage_isquash_tournament.py --headless --seed --extract-registrations %SNAPSHOTDIR%\TIMESTAMP-registrations.xls
python split_off_waitinglist.py --cutoff %1 %OUTOPT% --delete-nodiff %SNAPSHOTDIR%\*-registrations.xls
