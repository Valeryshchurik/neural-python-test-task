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

start_sync_mode:
	docker-compose up sync_processor

start_async_mode:
	docker-compose up async_processor

stop:
	docker-compose down