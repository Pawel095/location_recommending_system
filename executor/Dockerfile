FROM hadoop-base:local_latest

RUN apt install -y chromium mc

RUN pip install poetry
RUN poetry config virtualenvs.create false

WORKDIR /app
COPY ./package/poetry.lock /app
COPY ./package/pyproject.toml /app
RUN poetry export --without-hashes | pip install -r /dev/stdin
COPY ./package /app
RUN poetry install --no-dev

COPY execute.bash /execute.bash
RUN chmod a+x /execute.bash

CMD ["/execute.bash"]
