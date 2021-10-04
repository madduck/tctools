#!/bin/sh
#
# rebuild.sh — rebuild the HTML files
#
# Copyright © 2021 martin f. krafft <m@rtin.kiwi>
# Released under the terms of the MIT Licence.
#
set -eu

exec "${0%/*}/tc2web.py" ../tc-export-fixed.xls
