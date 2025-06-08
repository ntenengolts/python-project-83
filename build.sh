#!/usr/bin/env bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

uv --version

uv venv
source .venv/bin/activate

uv sync

psql -a -d "$DATABASE_URL" -f database.sql
