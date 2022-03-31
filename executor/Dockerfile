FROM hadoop-base:local_latest

RUN apt install -y chromium

RUN pip install poetry

WORKDIR /app
COPY ./package/poetry.lock /app
COPY ./package/pyproject.toml /app
RUN poetry export --without-hashes | pip install -r /dev/stdin


CMD ["sleep","infinity"]
