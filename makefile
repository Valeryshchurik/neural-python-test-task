env:
ifeq ($(OS),Windows_NT)
	@if not exist .env ( \
		echo OPENAI_API_KEY=""  # Insert your OpenAI API key here before starting > .env && \
		echo .env file created \
	)
else
	@if [ ! -f .env ]; then \
		echo 'OPENAI_API_KEY=""  # Insert your OpenAI API key here before starting' > .env; \
		echo ".env file created"; \
	fi
endif

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down