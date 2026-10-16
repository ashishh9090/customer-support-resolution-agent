.PHONY: setup install migrate seed test eval run-backend run-frontend dev clean

PYTHON=./venv/bin/python
PIP=./venv/bin/pip
ALEMBIC=./venv/bin/alembic
PYTEST=./venv/bin/pytest

setup:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt
	cd frontend && npm install

migrate:
	PYTHONPATH=. $(ALEMBIC) -c backend/alembic.ini upgrade head

seed:
	PYTHONPATH=. $(PYTHON) scripts/build_knowledge_index.py
	PYTHONPATH=. $(PYTHON) scripts/seed_database.py

test:
	PYTHONPATH=. $(PYTEST) backend/tests/ -v

eval:
	PYTHONPATH=. $(PYTHON) evaluation/run_evaluation.py

run-backend:
	PYTHONPATH=. $(PYTHON) -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

dev:
	PYTHONPATH=. $(PYTHON) scripts/run_dev.py

clean:
	rm -rf test_support_agent.db support_agent.db .pytest_cache/
