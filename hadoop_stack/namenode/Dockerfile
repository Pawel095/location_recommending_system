FROM hadoop-base:local_latest

EXPOSE 9870

HEALTHCHECK --start-period=300s CMD curl -f http://localhost:9870/ || exit 1

ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/name
RUN mkdir -p /hadoop/dfs/name
VOLUME /hadoop/dfs/name

COPY execute.bash /execute.bash
RUN chmod a+x /execute.bash

CMD ["/execute.bash"]
