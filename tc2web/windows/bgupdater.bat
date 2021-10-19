:: bgupdater.bat — screenshot the display, and upload changes
::
:: Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence
::
:: Look, this is Windows, and I know nothing about how stuff is supposed to
:: work on this platform. I don't even know why anyone would want to work with
:: this stuff ;)
:: If you know of a better way, please!
::
@echo off
setlocal

set "FILES=display.css display.html index.html live.html style.css games.html schedule.html draws.html"

cd /d %~dp0"

:: Infinite loop jump point
:again

if not exist "upload" (
  md upload
)

:: I have no idea how to check whether a file has been updated on Windows. So
:: the hack is to only process the exported file if it exists, and remove
:: it when we're done… until TC exports a new version.
if exist "..\..\tc-export.xls" (

  call fix-tc-export.bat
  del ..\..\tc-export.xls

  call rebuild.bat
)

call screenshot.bat %~dp0\display.png

for %%a in (%FILES%) do (
  xcopy /m /y /i ..\%%a upload
)
xcopy /i /y /m display.png upload

call upload.bat upload\* || (
  echo No upload.creds file, so skipping upload
)

del /q upload\*

choice /c qa /t 30 /n /d a /m "Waiting 30 seconds; hit 'a' to run again, or 'q' to quit"
if ERRORLEVEL 2 goto again
