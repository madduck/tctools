:: fix-tc-export.bat
::
:: Fix a file exported from TournamentControl (which uses an ancient Excel
:: format not supported by the tools here)
::
:: Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence.
::
@echo off
setlocal

set SOFFICE="\Program Files\Libreoffice\program\soffice.com"

set "CALLDIR=%CD%"
cd "%~dp0\..\.."

%SOFFICE% --convert-to ods tc-export.xls
move tc-export.ods tc-export-fixed.ods
%SOFFICE% --convert-to xls tc-export-fixed.ods
del tc-export-fixed.ods

cd "%CALLDIR%"
