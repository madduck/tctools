:: bgupdater.bat — screenshot the display, and upload changes
::
:: Copyright © 2021 martin f. krafft <tctools@pobox.madduck.net>
:: Released under the terms of the MIT Licence
::
:: This expects a file upload.creds in the local directory with the credentials
:: to use for FTP access:
::   FTPUSER='username'
::   FTPPASS='password'
::   FTPHOST='ftp.example.org'
::   TARGETDIR='/tc/'
::
:: You MUST USE THE SINGLE QUOTES around the parameters, and if your password
:: contains a single quote, I don't know what will happen.
::
@echo off
setlocal enableExtensions enableDelayedExpansion

if not exist "%~dp0%upload.creds" (
  echo The file %~dp0%upload.creds is missing >&2
  exit 1
)

for /F "eol=; tokens=1,2* delims==" %%i in (%~dp0%upload.creds) do (
    set "t=%%~j"
    set "%%i=!t:'=!"
)

ncftpput.exe -u %FTPUSER% -p %FTPPASS% %FTPHOST% %TARGETDIR% %*
