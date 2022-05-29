FROM hadoop-base:local_latest

EXPOSE 9864

HEALTHCHECK --start-period=300s CMD curl -f http://localhost:9864/ || exit 1

ENV HDFS_CONF_dfs_datanode_data_dir=file:///hadoop/dfs/data
RUN mkdir -p /hadoop/dfs/data
VOLUME /hadoop/dfs/data

COPY execute.bash /execute.bash
RUN chmod a+x /execute.bash

CMD ["/execute.bash"]
