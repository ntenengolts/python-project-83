install:
	uv sync

build:
	./build.sh

run:
	uv run flask --app page_analyzer:app run --host=0.0.0.0 --port=$$PORT

lint:
	uv run ruff check .

test:
	uv run pytest
