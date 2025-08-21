# Simple Makefile for RTSC Protocol

PYTHON=python

.PHONY: test install clean demo analyze

test:
	pytest

install:
	pip install -r requirements.txt

clean:
	rm -rf out/demo out/analysis .pytest_cache .mypy_cache __pycache__ */__pycache__

demo:
	$(PYTHON) quantum_rtsc_protocol/tools/rtsc_pipeline.py --demo --out out/demo

analyze:
	@if [ -z "$(in)" ]; then \
		echo "Usage: make analyze in=input.json"; \
		exit 1; \
	fi
	$(PYTHON) quantum_rtsc_protocol/tools/rtsc_pipeline.py --analyze $(in) --out out/analysis
