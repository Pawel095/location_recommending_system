FROM postgres:13

RUN apt update
RUN apt install -y --no-install-recommends \
    postgresql-plpython3-13 \
    postgresql-13-postgis \
    postgresql-13-postgis-scripts 
COPY enable-plpython3.sh /docker-entrypoint-initdb.d/plpython3.sh
COPY enable-postgis.sh /docker-entrypoint-initdb.d/postgis.sh
COPY postgresql.conf /