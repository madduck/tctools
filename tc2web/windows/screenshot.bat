:: screenshot.bat — Create a screenshot of the Tournament Display
::
:: TODO: Figure out how to crop the border of the screenshot
::
:: Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence
::
@echo off

qprocess TournControl.exe >NUL 2>&1
if %ERRORLEVEL% equ 0 (
  "\Program Files (x86)\MiniCap\MiniCap.exe" -save %~f1 -captureappbyname "TournControl.exe" -noerr -closeapp -exit -nofocus
) else (
  echo TournamentControl is not running. >&2
)

