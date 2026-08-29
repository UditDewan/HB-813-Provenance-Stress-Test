PY := uv run python

.PHONY: corpus sweep report test all clean

corpus:
	$(PY) -m src.corpus fetch
	$(PY) -m src.corpus verify

sweep: corpus
	$(PY) -m src.sweep

report: sweep
	$(PY) -m src.report

test:
	uv run pytest -q

all: report test

# Derived images only. Never data/results/runs.csv -- that is the evidence.
clean:
	rm -rf data/derived
