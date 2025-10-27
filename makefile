lock:
	docker run --rm -v $pwd:/src -w /src python:3.12 /bin/sh -c "\
		curl -sSL https://install.python-poetry.org | python3 - && \
		export PATH=$$HOME/.local/bin:$$PATH && \
		poetry lock"

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down