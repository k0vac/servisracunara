#!/bin/sh
set -e

python wait_for_db.py
alembic upgrade head
python seed.py
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
