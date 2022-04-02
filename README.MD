# magister

> HEAVILY INSPIRED BY: big-data-europe repositories at <https://github.com/big-data-europe>.

To acquire the map use <https://github.com/adrianulbona/osm-parquetizer> do build the parquet file. next copy the files to `./executor/package/map/`

## How to run

1. `prepare.bash` will build the base image
2. `docker compose up --build` will build and create all necesary containers.
3. `getExecutorShell.bash` and `prepopulateHDFS.bash` to upload required files to the hdfs

Run `getExecutorShell.bash` to get the shell inside the docker network, to run pyspark apps
