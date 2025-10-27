FROM python:3.12

# Устанавливаем poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && export PATH="$HOME/.local/bin:$PATH" \
    && poetry config virtualenvs.create false

WORKDIR /src

# Копируем pyproject.toml (без poetry.lock)
COPY pyproject.toml /src/

# Генерируем poetry.lock внутри контейнера
RUN $HOME/.local/bin/poetry lock

RUN $HOME/.local/bin/poetry install --no-interaction --no-ansi

# Копируем исходный код
COPY . /src