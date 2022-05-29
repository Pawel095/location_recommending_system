FROM postgres:13

RUN apt update
RUN apt install -y --no-install-recommends \
    postgresql-plpython3-13
COPY enable-plpython3.sh /docker-entrypoint-initdb.d/plpython3.sh
RUN chmod +x /docker-entrypoint-initdb.d/plpython3.sh
COPY postgresql.conf /