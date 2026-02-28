# Things to Implement and Fix

[x] Update the FLAC check process to also include path and filename information about the input files into the Redis database.
[x] Impelment a web interface (based on Flask) to query and visualize the results in Redis.
    [x] Add a new container build process that will run this interface.  Use existing patterns for build and publish of a container.
    [x] Update the Kubernetes deployment to run this service.
