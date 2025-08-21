# Simple Makefile for RTSC Protocol

PYTHON=python

.PHONY: demo analyze clean

demo:
\t$(PYTHON) tools/rtsc_pipeline.py --demo --out out/demo

analyze:
\t@if [ -z "$(in)" ]; then \\
\t\techo "Usage: make analyze in=input.json"; \\
\t\texit 1; \\
\tfi
\t$(PYTHON) tools/rtsc_pipeline.py --analyze $(in) --out out/analysis

clean:
\trm -rf out/demo out/analysis
