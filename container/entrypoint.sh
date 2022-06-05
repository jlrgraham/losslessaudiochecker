#!/bin/bash

set -o xtrace

if [ -z "${PARALLEL}" ]; then
    PARALLEL=1
fi

find /input -type f -name \*.flac -print0 \
    | xargs --null --no-run-if-empty -P${PARALLEL} -I{} /usr/local/bin/check-flac-file.sh {}
