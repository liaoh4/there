#!/bin/sh
alembic upgrade head
python data/scripts/seed.py
uvicorn app.main:app --host 0.0.0.0 --port 8000