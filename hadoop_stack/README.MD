# magister

> HEAVILY INSPIRED BY: big-data-europe repositories at <https://github.com/big-data-europe>.

To acquire the map use <https://github.com/adrianulbona/osm-parquetizer> do build the parquet file. next copy the files to `./executor/package/map/`

## How to run

1. `cd hadoop_stack`
2. `./prepare.bash --no-cache -p` will build and push the images
3. `docker compose up` or `./deploy up` to start the stack standalone or in a swarm respectively.
4. `getExecutorShell.bash` and `prepopulateHDFS.bash` to upload required files to the hdfs, prepare the data and build the ALS model.

Run `getExecutorShell.bash` to get the shell inside the docker network, to run pyspark apps
To build the models, about 15 gigabytes of ram and about 130 gb of disk space is required. SSD drive reccomended
