:: screenshot.bat — Create a screenshot of the Tournament Display
::
:: TODO: Figure out how to crop the border of the screenshot
::
:: Copyright © 2021–2022 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence
::
@echo off

set TCexe=TournControl.exe
tasklist /NH /FI "ImageName eq %TCexe%" | findstr /i "%TCexe%" >NUL 2>&1
if %ERRORLEVEL% equ 0 (
  "\Program Files (x86)\MiniCap\MiniCap.exe" -save %~f1 -captureappbyname "%TCexe%" -noerr -closeapp -exit -nofocus
) else (
  echo TournamentControl is not running. >&2
)

