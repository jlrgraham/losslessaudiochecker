FROM debian

RUN --mount=type=cache,target=/var/cache/apt \
    apt update \
    && apt install -y flac redis-tools \
    && apt clean

COPY LAC-Linux-64bit /usr/local/bin/LAC
COPY check-flac-file.sh /usr/local/bin/check-flac-file.sh
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
