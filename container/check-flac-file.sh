#!/bin/bash

set -o errexit

if [ -z "${1}" ]; then
    echo "Usage: $0 <path_to.flac>"
    exit 1
fi

INPUT_FILE="${1}"
TEMP_WAV="/tmp/input-$$.wav"
LAC_RESULTS="${TEMP_WAV}.results"


FSTAT=$(stat --format=%b-%Y "${INPUT_FILE}")
INPUT_BASENAME=$(basename "${INPUT_FILE}")

REDIS_HASH=$(echo "${FSTAT} ${INPUT_BASENAME}" | sha256sum | cut -d" " -f1)

if [ -n "${REDIS_HOST}" ]; then
    CACHED_RESULT=$(redis-cli -h ${REDIS_HOST} GET ${REDIS_HASH})

    if [ -n "${CACHED_RESULT}" ]; then
        echo "Cache hit: ${INPUT_FILE} : ${CACHED_RESULT}"
        exit 0
    fi

    # Try to lock for processing of this file
    PROCESS_LOCK=$(redis-cli -h ${REDIS_HOST} SET ${REDIS_HASH}-lock "true" NX EX 60)
    if [ "x${PROCESS_LOCK}" != "xOK" ]; then
        echo "Could not obtain processing lock: ${INPUT_FILE}"
        exit 0
    else
        echo "Issued 60 second processing lock: ${INPUT_FILE}"
    fi
fi

# Convert to WAV for analysis
flac \
    --decode \
    --silent \
    --output-name "${TEMP_WAV}" \
    "${INPUT_FILE}"

# Check the file
/usr/local/bin/LAC "${TEMP_WAV}" > "${LAC_RESULTS}"

# Get the result out of the output
RESULT=$(awk '/^Result: .*/ {print $2}' "${LAC_RESULTS}")

if [ -n "${REDIS_HOST}" ]; then
    redis-cli -h ${REDIS_HOST} SET ${REDIS_HASH} ${RESULT}
fi

if [ "x${RESULT}" != "xClean" ]; then
    echo "Not clean: ${INPUT_FILE}"
    cat "${LAC_RESULTS}"
else
    echo "Clean: ${INPUT_FILE}"
fi

# Tidy tidy
rm -f "${TEMP_WAV}"
