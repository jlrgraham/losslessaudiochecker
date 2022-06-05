#!/bin/bash

set -o xtrace

find /input -type f -name \*.flac -print0 | xargs -0 -I{} /usr/local/bin/check-flac-file.sh {}
