FROM python:3.12

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    $HOME/.local/bin/poetry config virtualenvs.create false

ENV PATH="$HOME/.local/bin:$PATH"

WORKDIR /src

COPY pyproject.toml /src/

RUN $HOME/.local/bin/poetry lock

RUN $HOME/.local/bin/poetry install --no-interaction --no-ansi

COPY . /src