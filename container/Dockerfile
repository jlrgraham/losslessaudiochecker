FROM debian

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update \
    && apt-get install -y curl flac redis-tools \
    && apt-get clean
RUN curl -L -o- https://losslessaudiochecker.com/dl/LAC-Linux-64bit.tar.gz | tar -C /usr/local/bin -x -z

COPY check-flac-file.sh /usr/local/bin/check-flac-file.sh
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
