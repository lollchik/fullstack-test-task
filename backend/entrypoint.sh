#!/bin/bash

alembic history
alembic upgrade head
alembic current

exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
