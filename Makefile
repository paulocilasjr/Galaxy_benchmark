PYTHON ?= python3

.PHONY: test scorer-test audit reliability

test:
	$(PYTHON) -m unittest discover -s tests/unit -v

scorer-test:
	$(PYTHON) tools/test_benchmark_scorer.py

audit:
	$(PYTHON) tools/audit_benchmark_assets.py

reliability:
	@echo "Use: python3 tools/build_reliability_report.py --run-record <path> [--run-record <path> ...]"
