FROM hadoop-base:local_latest

EXPOSE 8042

HEALTHCHECK CMD curl -f http://localhost:8042/ || exit 1

COPY execute.bash /execute.bash
RUN chmod a+x /execute.bash

CMD ["/execute.bash"]
