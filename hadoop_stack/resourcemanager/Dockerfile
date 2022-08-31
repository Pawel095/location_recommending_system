FROM hadoop-base:local_latest

EXPOSE 8088

HEALTHCHECK --start-period=300s CMD curl -f http://localhost:8088/ || exit 1

COPY execute.bash /execute.bash
RUN chmod a+x /execute.bash

CMD ["/execute.bash"]