# Dockerized Lossless Audio Checker

Just packages up [Lossless Audio Checker](https://losslessaudiochecker.com/) for use in Docker.

Usage, invoke the container with the target files to check mounted to `/input`.

If the enviornmental variable `REDIS_HOST` is set then the script will:

1. Generate an identifier hash of the file (SHA256 of `<file_size>-<file_mod_epoch> <filename>`).
2. Store the output element of `LAC` (ie: `Clean`).