# Things to Implement and Fix

[x] Update the FLAC check process to also include path and filename information about the input files into the Redis database.
[x] Impelment a web interface (based on Flask) to query and visualize the results in Redis.
    [x] Add a new container build process that will run this interface.  Use existing patterns for build and publish of a container.
    [x] Update the Kubernetes deployment to run this service.
[x] Add the ability to filter the results in the web interface by clean / not-clean.
[x] Add a report on a path prefix that shows if all the contents are clean or not.  For example /input/album1/file1.flac and /input/album1/file2.flac.
