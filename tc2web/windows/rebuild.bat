:: rebuild.bat — Rebuild the HTML pages
::
:: Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence
::
@echo off

set "CALLDIR=%CD%"
cd %~dp0\..
python.exe tc2web.py ..\tc-export-fixed.xls
cd %CALLDIR%