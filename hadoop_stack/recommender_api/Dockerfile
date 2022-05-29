FROM hadoop-base:local_latest

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY ./poetry.lock /app
COPY ./pyproject.toml /app
RUN poetry export --without-hashes --dev | pip3 install -r /dev/stdin
COPY . /app
RUN poetry install
