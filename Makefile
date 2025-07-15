install:
	uv sync

build:
	./build.sh

run:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check .

test:
	uv run pytest
