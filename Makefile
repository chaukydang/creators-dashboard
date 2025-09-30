.PHONY: setup lint fix test run clean-data
setup:
\tpython -m venv .venv && . .venv/bin/activate && pip install -r app/requirements.txt
lint:
\truff check . && python -m black --check . && isort --check-only .
fix:
\truff check . --fix && isort . && python -m black .
test:
\tpytest -q
run:
\tstreamlit run app/App.py
clean-data:
\tpython scripts/kol_cleaner.py
