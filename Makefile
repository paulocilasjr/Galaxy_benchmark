PYTHON ?= python3

.PHONY: test scorer-test audit reliability publication-results release-packages

test:
	$(PYTHON) -m unittest discover -s tests/unit -v

scorer-test:
	$(PYTHON) tools/test_benchmark_scorer.py

audit:
	$(PYTHON) tools/audit_benchmark_assets.py

reliability:
	@echo "Use: python3 tools/build_reliability_report.py --run-record <path> [--run-record <path> ...]"

publication-results:
	$(PYTHON) tools/build_publication_results_bundle.py

release-packages:
	$(PYTHON) tools/build_release_packages.py --output-dir /tmp/galaxy_benchmark_release
