#!/usr/bin/env bash

uv --version
uv venv
uv sync
psql -a -d "$DATABASE_URL" -f database.sql
