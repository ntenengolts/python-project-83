install-uv:
	curl -LsSf https://astral.sh/uv/install.sh | sh
	export PATH="$$HOME/.local/bin:$$PATH

install: install-uv
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	.venv/bin/gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

lint:
	uv run ruff check .

build:
	./build.sh
