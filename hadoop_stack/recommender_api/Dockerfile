FROM hadoop-base:local_latest

HEALTHCHECK --start-period=300s --retries=5 CMD curl -f http://localhost:8888/healthcheck || exit 1

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY ./poetry.lock /app
COPY ./pyproject.toml /app
COPY ./geomesa_pyspark-3.4.0.tar.gz /app
RUN poetry export --without-hashes | pip3 install -r /dev/stdin
COPY . /app
RUN poetry install --no-dev